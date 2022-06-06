#!/usr/bin/env python3
# Copyright 2019 Alexander Meulemans
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Controller for simulations
--------------------------

The module :mod:`main` is an executable script that controls the simulations.

For more usage information, please check out

.. code-block:: console

  $ python3 main --help

"""
import argparse
import json
from typing import Dict, List, Optional
import numpy as np
import random
import torch
import torchvision
import torchvision.transforms as transforms
import os

from typing import Literal
from tensorboardX import SummaryWriter
import os.path
import pickle

try:
    from .lib.train import train, train_bp
    from .lib import utils
    from .lib import builders
except ImportError:
    from lib.train import train, train_bp
    from lib import utils
    from lib import builders

# TODO: Local fix for mac
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

NetworkName = Literal[
    "DTP",
    "LeeDTP",
    "DTPDR",
    "DKDTP2",
    "DMLPDTP2",
    "BP",
    "GN2",
    "DFA",
    "DDTPControl",
    "DDTPConv",
    "DFAConv",
    "BPConv",
    "DDTPConvCIFAR",
    "DFAConvCIFAR",
    "BPConvCIFAR",
    "DDTPConvControlCIFAR",
]


def run(overwrite_defaults: Optional[dict] = None):
    """
    - Parsing command-line arguments
    - Creating synthetic regression data
    - Initiating training process
    - Testing final network

    """
    parser = add_command_line_args()
    if overwrite_defaults is not None:
        parser.set_defaults(**overwrite_defaults)

    args = parser.parse_args()

    args = postprocess_args(args)

    return launch(args)


import simple_parsing
from simple_parsing import choice, ArgumentParser, field, list_field
from simple_parsing.helpers.serialization.serializable import Serializable
from simple_parsing.helpers.flatten import FlattenedAccess
from dataclasses import dataclass


@dataclass
class DatasetOptions(Serializable):
    """Dataset options"""

    # Used dataset for classification/regression.
    dataset: str = choice("mnist", "student_teacher", "fashion_mnist", "cifar10", default="cifar10")
    # Number of training samples used for the student teacher regression.
    num_train: int = 1000

    num_test: int = 1000
    """Number of test samples used for the student teacher regression. """

    num_val: int = 1000
    """Number of validation samples used for the student teacher regression."""


@dataclass
class TrainOptions(Serializable):
    """Training options"""

    epochs: int = 90
    """ Number of training epochs. """

    batch_size: int = 100
    """ Training batch size. Choose divisor of "num_train". """

    lr: list[float] = list_field(0.01)
    """ Learning rate of optimizer for the forward parameters. You can either provide a single float
    that will be used as lr for all the layers, or a list of learning rates (e.g. [0.1,0.2,0.5]) 
    specifying a lr for each layer. The lenght of the list should be equal to num_hidden + 1.
    The list may not contain spaces.
    """

    lr_fb: float = 0.000101149118237
    """ Learning rate of optimizer for the feedback parameters. """

    nb_feedback_iterations: list[int] = list_field(1)
    """ Number of feedback weight training iterations per batch, *for each layer*. """

    target_stepsize: float = 0.01
    """ Step size for computing the output target based on the output gradient. """

    optimizer: str = choice("SGD", "RMSprop", "Adam", default="SGD")
    """ Optimizer used for training. """

    optimizer_fb: Optional[str] = choice(None, "SGD", "RMSprop", "Adam", default=None)
    """ Optimizer used for training the feedback parameters. """
    momentum: float = 0.9
    """ Momentum of the SGD or RMSprop optimizer. """
    sigma: float = 0.08
    """ Svd of gaussian noise used to corrupt the hidden layer activations for computing the 
    reconstruction loss.
    """
    forward_wd: float = 0.0
    """ Weight decay for the forward weights. """
    feedback_wd: float = 0.0
    """ Weight decay for the feedback weights. """
    train_separate: bool = False
    """Flag indicating that first the feedback parameters are trained on a whole epoch, after which
    the forward parameters are trained for a whole epoch like in Lee2015. """
    parallel: bool = False
    """Depreciated argument. The opposite of `train_separate`."""
    not_randomized: bool = False
    """Depreciated argument. Flag indicating that the randomized target propagation training scheme
    should not be used.
    """
    train_randomized: bool = False
    """ Flag indicating that the randomized target propagation training scheme should be used, 
    where for each minibatch, one layer is selected randomly for updating.
    """

    normalize_lr: bool = False
    """Flag indicating that we should take the real learning rate of the forward parameters to be:
    lr=lr/target_stepsize. This makes the hpsearch easier, as lr and target_stepsize have similar
    behavior.
    """
    train_only_feedback_parameters: bool = False
    """ Flag indicating that only the feedback parameters should be trained, not the forward 
    parameters.
    """
    epochs_fb: int = 1
    """Number of training epochs. """

    soft_target: float = 0.9
    """Used in combination with sigmoid output activation and L2 output loss. Instead of using
    one-hot vectors as output labels, we multiply the one hot vector with soft_target such that the 
    network does not push its output to extreme values. 
    """

    freeze_forward_weights: bool = False
    """Only train the feedback weights, the forward weights stay fixed. We still compute the targets
    to update the forward weights, such that they can be logged and investigated.
    """

    freeze_fb_weights: bool = False
    """Only train the forward parameters, the feedback parameters stay fixed. When combined
    with linear feedback activation functions, this is similar to feedback alignment
    """

    shallow_training: bool = False
    """Train only the parameters of the last layer and" "let the others stay fixed."""

    norm_ratio: float = 1.0
    """Hyperparameter used for computing the minimal norm update of the parameters, given the
    targets.
    """

    extra_fb_epochs: int = 0
    """ After each epoch of training, the fb parameters will be trained for an extra
    `extra_fb_epochs` 
    """

    extra_fb_minibatches: int = 0
    """After each minibatch training of the forward parameters, we do <N> extra minibatches training
    for the feedback weights. The extra minibatches are randomly sampled from the trainingset
    """

    freeze_output_layer: bool = False
    """Freeze the forward parameters of the output layer and only train the forward parameters of
    the hidden layers. The feedback parameters of all layers are still trained.
    """

    gn_damping_training: float = 0.0
    """ Thikonov damping used to train the GN network. """

    not_randomized_fb: bool = False
    """ Depreciated argument. 
    This flag applies for networks that use the difference reconstruction loss. The flag indicates
    that for each minibatch, all feedback parameters should be trained instead of only one set of
    randomly drawn feedback parameters.
    """

    train_randomized_fb: bool = False
    """This flag applies for networks that use the difference reconstruction loss. The flag
    indicates that for each minibatch, one layer is selected randomly for training the feedback 
    parameters.
    """

    only_train_first_layer: bool = False
    """Only train the forward parameters of the first layer, while freezing all other forward
    parameters to their initialization. The feedback parameters are all trained.
    """

    no_val_set: bool = False
    """ Flag indicating that no validation set is used during training. """

    no_preprocessing_mnist: bool = False
    """Take the mnist input values between 0 and 1, instead of standardizing them. """

    loss_scale: float = 1.0
    """Depreciated. Scale the loss by this factor to mitigate numerical problems."""

    only_train_last_two_layers: bool = False
    """ Only train the last two layers of the network."""

    only_train_last_three_layers: bool = False
    """ Only train the last three layers of the network. """

    only_train_last_four_layers: bool = False
    """Only train the last four layers of the network."""


@dataclass
class AdamOptions(Serializable):
    """Training options for the Adam optimizer."""

    beta1: float = 0.99
    """ beta1 training hyperparameter for the adam optimizer. """

    beta2: float = 0.99
    """ beta2 training hyperparameter for the adam optimizer. """

    epsilon: list[float] = field(default_factory=[1e-4].copy)
    """epsilon training hyperparameter for the adam optimizer. """

    beta1_fb: float = 0.99
    """beta1 training hyperparameter for the adam feedback optimizer. """

    beta2_fb: float = 0.99
    """beta2 training hyperparameter for the adam feedback optimizer. """

    epsilon_fb: float = 1e-4
    """epsilon training hyperparameter for the adam feedback optimizer. """


@dataclass
class NetworkOptions(Serializable):
    """Network options"""

    hidden_layers: Optional[List[int]] = None
    """ Number of hidden layers. """
    # help='Number of hidden layer in the (student) ' +
    #      'network. Default: %(default)s.')

    num_hidden: int = 2
    """ Number of hidden layer in the network. """

    size_hidden: List[int] = list_field(500)
    """ Number of units in each hidden layer of the (student) network. If you provide a list, you 
    can have layers of different sizes.
    """

    size_input: int = 3072
    """ Number of units of the input. """

    size_output: int = 10
    """ Number of units of the output """

    size_hidden_fb: int = 500
    """ Number of units of the hidden feedback layer (in the DDTP-RHL variants). """

    hidden_activation: str = choice(
        "tanh", "relu", "linear", "leakyrelu", "elu", "sigmoid", default="tanh"
    )
    """ Activation function used for the hidden layers. """

    output_activation: str = choice(
        "tanh", "relu", "linear", "leakyrelu", "elu", "sigmoid", "softmax", default="softmax"
    )
    """Activation function used for the output. """

    fb_activation: Optional[str] = choice(
        "tanh", "relu", "linear", "leakyrelu", "elu", "sigmoid", default=None
    )
    """ Activation function used for the feedback targets for the hidden layers. Default the same as
    hidden_activation.
    """

    no_bias: bool = False
    """ Flag for not using biases in the network. """

    network_type: str = choice(
        "DTP",
        "LeeDTP",
        "DTPDR",
        "DKDTP2",
        "DMLPDTP2",
        "BP",
        "GN2",
        "DFA",
        "DDTPControl",
        "DDTPConv",
        "DFAConv",
        "BPConv",
        "DDTPConvCIFAR",
        "DFAConvCIFAR",
        "BPConvCIFAR",
        "DDTPConvControlCIFAR",
        default="DDTPConvCIFAR",
    )
    """ Variant of TP that will be used to train the network. See the layer classes for explanations 
    of the names.
    """

    initialization: str = choice(
        "orthogonal", "xavier", "xavier_normal", "teacher", default="xavier_normal"
    )
    """ Type of initialization that will be used for the forward and feedback weights of the
    network.
    """

    size_mlp_fb: list[int] = list_field(100)
    """ The size of the hidden layers of the MLP that is used in the DMLPDTP layers.
    """
    # NOTE: Removed this:
    # For one hidden layer, provide the integer indicating the size of the
    # hidden layer. For multiple hidden layers, provide a list with all layer sizes, separated by ",",
    # without spaces and encapsulated by "[]". If you dont want any hidden layers, give None.

    hidden_fb_activation: Optional[str] = choice(
        "tanh", "relu", "linear", "leakyrelu", "sigmoid", default=None
    )
    """Activation function used for the hidden layers of the direct feedback mapping. """

    recurrent_input: bool = False
    """ Flag indicating whether the direct feedback mapping should also use the nonlinear activation
    of the current layer as input to improve the feedback mapping.
    """


@dataclass
class MiscOptions(Serializable):
    """Miscellaneous options."""

    no_cuda: bool = False
    """ Flag to disable GPU usage. """
    random_seed: int = 42
    """ Random seed. """

    cuda_deterministic: bool = False
    """ Flag to make the GPU computations deterministic. note: this slows down computation! """

    freeze_BPlayers: bool = False
    """ Flag to freeze the parameters of the output layer and the last hidden layer, that normally
    are trained with BP in the LeeDTP network, to see if DTP transmits useful teaching signals.
    """
    hpsearch: bool = False
    """ Flag indicating that the main script is running in the context of a hyper parameter search.
    """

    multiple_hpsearch: bool = False
    """ Flag indicating that main is runned in the `context of multiple_hpsearches.py`."""

    double_precision: bool = False
    """ Use double precision floats (64bits) instead of 32bit floats to increase the precision of
    the computations. This slows down training.
    """
    evaluate: bool = False
    """ Don't stop unpromising runs, because we are evaluating hp parameter results."""


@dataclass
class LoggingOptions(Serializable):
    """Logging options."""

    out_dir: str = "logs"
    """ Relative path to directory where the logs are saved. """

    save_logs: bool = False
    """ Flag to save logs and plots by using tensorboardX. """

    save_BP_angle: bool = False
    """Flag indicating whether the BP updates and the angle between those updates and the TP updates
    should be computed and saved.
    """

    save_GN_angle: bool = False
    """
    Flag indicating whether the GN updates and the angle between those updates and the TP updates
    should be computed and saved. Warning: this causes a heavy extra computational load.
    """

    save_GNT_angle: bool = False
    """ Flag inidcating whether angle with the ideal GNT updates should be computed. Warning, this
    causes a heavy extra computational load.
    """

    save_GN_activations_angle: bool = False
    """
    Flag indicating whether the Gauss-Newton updates for the layer activations should be computed
    and the angle with the TP updates for the activations should be computed and saved. Warning:
    this causes a heavy extra computational load.
    """

    save_BP_activations_angle: bool = False
    """ Flag indicating whether the BP updates for the layer activations should be computed and
    the angle with the TP updates for the activations should be computed and saved.
    """

    plots: Optional[str] = choice(None, "save", "save_and_show", "compute", default="save")

    save_loss_plot: bool = False
    """ Save a plot of the test loss and the training loss. """

    create_plots: bool = False
    """ Flag indicating whether the angles should be plotted and saved. """

    gn_damping: float = 0.0
    """ Thikonov damping used for computing the  Gauss-Newton updates that are used to compute the
    angles between the actual updates and the GN updates. "
    """

    log_interval: Optional[int] = None
    """ Each `log_interval` batches, the batch results are logged to tensorboard."""

    output_space_plot: bool = False
    """Make a plot of the trajectory of the output in the output space accompagnied by loss
    contours.
    """

    output_space_plot_layer_idx: Optional[int] = None
    """ Layer index for making the output_space_plot. """

    output_space_plot_bp: bool = False
    """ plot the output space update for a BP update."""

    save_weights: bool = False
    load_weights: bool = False

    gn_damping_hpsearch: bool = False
    """Flag indicating whether a small hpsearch should be performed to optimize the gn_damping 
    constant with which the gnt angles are computed.
    """

    save_nullspace_norm_ratio: bool = False
    """Flag indicating whether the norm ratio between the nullspace components of the parameter 
    updates and the updates themselves should be computed and saved.
    """


@dataclass
class Args(DatasetOptions, TrainOptions, AdamOptions, NetworkOptions, MiscOptions, LoggingOptions):
    """Command-line options.

    NOTE: Typed equivalent to all the code below. Using docstrings for the fields makes it possible
    to see directly the description of each argument when hovering over it in most editors e.g.
    vscode.
    """

    # TODO: Would be nice to have these, instead of having everything at the same level.
    # dataset: DatasetOptions = field(default_factory=DatasetOptions)
    # training: TrainOptions = field(default_factory=TrainOptions)
    # adam: AdamOptions = field(default_factory=AdamOptions)
    # network: NetworkOptions = field(default_factory=NetworkOptions)
    # misc: MiscOptions = field(default_factory=MiscOptions)
    # logging: LoggingOptions = field(default_factory=LoggingOptions)

    def __post_init__(self):
        self.save_angle = (
            self.save_GN_activations_angle
            or self.save_BP_activations_angle
            or self.save_BP_angle
            or self.save_GN_angle
            or self.save_GNT_angle
        )
        print(self)

        ### Create summary log writer
        curdir = os.path.curdir
        if self.out_dir is None:
            out_dir = os.path.join(
                curdir,
                "logs",
            )
            self.out_dir = out_dir
        else:
            out_dir = os.path.join(curdir, self.out_dir)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
        print("Logging at {}".format(out_dir))

        with open(os.path.join(out_dir, "self.txt"), "w") as f:
            json.dump(self.__dict__, f, indent=2)

        self.classification = self.dataset in ["mnist", "fashion_mnist", "cifar10"]
        self.regression = self.dataset in ["student_teacher", "boston"]
        if not self.classification and not self.regression:
            raise ValueError("Dataset {} is not supported.".format(self.dataset))

        # initializing command line arguments if None
        self.output_activation = self.output_activation or (
            "softmax" if self.classification else "linear"
        )

        self.fb_activation = self.fb_activation or self.hidden_activation
        self.hidden_fb_activation = self.hidden_fb_activation or self.hidden_activation
        self.optimizer_fb = self.optimizer_fb or self.optimizer

        # Manipulating command line arguments if asked
        # TODO: They were manipulating these if they were strings, which isn't necessary anymore,
        # however, it might be important to be able to load from their configs in the long run.
        if isinstance(self.lr, str):
            self.lr = utils.process_lr(self.lr)
        if isinstance(self.lr_fb, str):
            self.lr_fb = utils.process_lr(self.lr_fb)
        if isinstance(self.nb_feedback_iterations, str):
            self.nb_feedback_iterations = utils.process_nb_feedback_iterations(
                self.nb_feedback_iterations
            )
        if isinstance(self.epsilon_fb, str):
            self.epsilon_fb = utils.process_lr(self.epsilon_fb)
        if isinstance(self.epsilon, str):
            self.epsilon = utils.process_lr(self.epsilon)
        if isinstance(self.size_hidden, str):
            self.size_hidden = utils.process_hdim(self.size_hidden)

        self.random_seed = int(self.random_seed)
        if self.size_mlp_fb == "None":
            self.size_mlp_fb = None
        elif isinstance(self.size_mlp_fb, str):
            self.size_mlp_fb = utils.process_hdim_fb(self.size_mlp_fb)

        if self.normalize_lr:
            self.lr = np.array(self.lr) / self.target_stepsize

        if self.network_type in ["GN", "GN2"]:
            # if the GN variant of the network is used, the fb weights do not need
            # to be trained
            self.freeze_fb_weights = True

        if self.network_type == "DFA":
            # manipulate cmd arguments such that we use a DMLPDTP2 network with
            # linear MLP's with fixed weights
            self.freeze_fb_weights = True
            self.network_type = "DMLPDTP2"
            self.size_mlp_fb = None
            self.fb_activation = "linear"
            self.train_randomized = False

        if self.network_type == "DFAConv":
            self.freeze_fb_weights = True
            self.network_type = "DDTPConv"
            self.fb_activation = "linear"
            self.train_randomized = False

        if self.network_type == "DFAConvCIFAR":
            self.freeze_fb_weights = True
            self.network_type = "DDTPConvCIFAR"
            self.fb_activation = "linear"
            self.train_randomized = False

        if self.network_type in ["DTPDR"]:
            self.diff_rec_loss = True
        else:
            self.diff_rec_loss = False

        if self.network_type in [
            "DKDTP",
            "DKDTP2",
            "DMLPDTP",
            "DMLPDTP2",
            "DDTPControl",
            "DDTPConv",
            "DDTPConvCIFAR",
            "DDTPConvControlCIFAR",
        ]:
            self.direct_fb = True
        else:
            self.direct_fb = False

        if isinstance(self.gn_damping, str) and "," in self.gn_damping:
            self.gn_damping = utils.str_to_list(self.gn_damping, type="float")
        else:
            self.gn_damping = float(self.gn_damping)

        # Checking valid combinations of command line arguments
        if self.shallow_training:
            if not self.network_type == "BP":
                raise ValueError(
                    "The shallow_training method is only implemented"
                    "in combination with BP. Make sure to set "
                    "the network_type argument on BP."
                )


def add_command_line_args_v2(parser: simple_parsing.ArgumentParser = None):
    ### Parse CLI arguments.
    parser = parser or simple_parsing.ArgumentParser(
        description='Run experiments from paper "A theoretical framework for target propagation".'
    )

    parser.add_arguments(Args, dest="")
    return parser


def add_command_line_args(parser: argparse.ArgumentParser = None):
    ### Parse CLI arguments.
    parser = parser or argparse.ArgumentParser(
        description="Run experiments from paper "
        '"A theoretical framework for'
        'target propagation".'
    )

    dgroup = parser.add_argument_group("Dataset options")
    dgroup.add_argument(
        "--dataset",
        type=str,
        default="cifar10",
        choices=["mnist", "student_teacher", "fashion_mnist", "cifar10"],
        help="Used dataset for classification/regression. " "Default: %(default)s.",
    )
    dgroup.add_argument(
        "--num_train",
        type=int,
        default=1000,
        help="Number of training samples used for the "
        "student teacher regression. "
        "Default: %(default)s.",
    )
    dgroup.add_argument(
        "--num_test",
        type=int,
        default=1000,
        help="Number of test samples used for the "
        "student teacher regression. "
        "Default: %(default)s.",
    )
    dgroup.add_argument(
        "--num_val",
        type=int,
        default=1000,
        help="Number of validation samples used for the"
        "student teacher regression. "
        "Default: %(default)s.",
    )

    tgroup = parser.add_argument_group("Training options")
    tgroup.add_argument(
        "--epochs",
        type=int,
        metavar="N",
        default=90,
        help="Number of training epochs. " + "Default: %(default)s.",
    )
    tgroup.add_argument(
        "--batch_size",
        type=int,
        metavar="N",
        default=100,
        help="Training batch size. " 'Choose divisor of "num_train". ' "Default: %(default)s.",
    )
    tgroup.add_argument(
        "--lr",
        type=str,
        default="0.01",
        help="Learning rate of optimizer for the forward "
        "parameters. You can either provide a single "
        "float that will be used as lr for all the layers,"
        "or a list of learning rates (e.g. [0.1,0.2,0.5]) "
        "specifying a lr for each layer. The lenght of the"
        " list should be equal to num_hidden + 1. The list"
        "may not contain spaces. Default: " + "%(default)s.",
    )
    tgroup.add_argument(
        "--lr_fb",
        type=str,
        default="0.000101149118237",
        help="Learning rate of optimizer for the feedback "
        "parameters. Default: " + "%(default)s.",
    )
    tgroup.add_argument(
        "--nb_feedback_iterations",
        type=str,
        default="1",
        help="Number of feedback weight training iterations per batch Default: " + "%(default)s.",
    )
    tgroup.add_argument(
        "--target_stepsize",
        type=float,
        default=0.01,
        help="Step size for computing the output target based"
        "on the output gradient. Default: " + "%(default)s.",
    )
    tgroup.add_argument(
        "--optimizer",
        type=str,
        default="SGD",
        choices=["SGD", "RMSprop", "Adam"],
        help="Optimizer used for training. Default: " "%(default)s.",
    )
    tgroup.add_argument(
        "--optimizer_fb",
        type=str,
        default=None,
        choices=[None, "SGD", "RMSprop", "Adam"],
        help="Optimizer used for training the feedback " "parameters.",
    )
    tgroup.add_argument(
        "--momentum",
        type=float,
        default=0.9,
        help="Momentum of the SGD or RMSprop optimizer. " + "Default: %(default)s.",
    )
    tgroup.add_argument(
        "--sigma",
        type=float,
        default=0.08,
        help="svd of gaussian noise used to corrupt the hidden"
        " layer activations for computing the "
        "reconstruction loss. Default: %(default)s.",
    )
    tgroup.add_argument(
        "--forward_wd",
        type=float,
        default=0.0,
        help="Weight decay for the forward weights. " "Default: %(default)s.",
    )
    tgroup.add_argument(
        "--feedback_wd",
        type=float,
        default=0.0,
        help="Weight decay for the feedback weights. " "Default: %(default)s.",
    )
    tgroup.add_argument(
        "--train_separate",
        action="store_true",
        help="Flag indicating that first"
        "the feedback parameters are trained on a whole"
        "epoch, after which the forward parameters are "
        "trained for a whole epoch like in Lee2015",
    )
    tgroup.add_argument(
        "--parallel",
        action="store_true",
        help="Depreciated argument. " 'The opposite of "train_separate".',
    )
    tgroup.add_argument(
        "--not_randomized",
        action="store_true",
        help="Depreciated argument."
        "Flag indicating that the randomized target "
        "propagation training scheme should not be used.",
    )
    tgroup.add_argument(
        "--train_randomized",
        action="store_true",
        help="Flag indicating that the randomized target "
        "propagation training scheme should be used,"
        "where for each minibatch, one layer is selected"
        "randomly for updating.",
    )
    tgroup.add_argument(
        "--normalize_lr",
        action="store_true",
        help="Flag indicating that we should take the real "
        "learning rate of the forward parameters to be:"
        "lr=lr/target_stepsize. This makes the hpsearch"
        "easier, as lr and target_stepsize have similar"
        "behavior.",
    )
    tgroup.add_argument(
        "--train_only_feedback_parameters",
        action="store_true",
        help="Flag indicating that only the feedback parameters"
        "should be trained, not the forward parameters.",
    )
    tgroup.add_argument(
        "--epochs_fb",
        type=int,
        metavar="N",
        default=1,
        help="Number of training epochs. " + "Default: %(default)s.",
    )
    tgroup.add_argument(
        "--soft_target",
        type=float,
        default=0.9,
        help="Used in combination with sigmoid output "
        "activation and L2 output loss. Instead of using "
        "one-hot vectors as output labels, we multiply the"
        "one hot vector with soft_target such that the "
        "network does not push its output to extreme "
        "values. Default: %(default)s.",
    )
    tgroup.add_argument(
        "--freeze_forward_weights",
        action="store_true",
        help="Only train the feedback weights, the forward "
        "weights stay fixed. We still compute the targets"
        "to update the forward weights, such that they "
        "can be logged and investigated.",
    )
    tgroup.add_argument(
        "--freeze_fb_weights",
        action="store_true",
        help="Only train the forward parameters, the "
        "feedback parameters stay fixed. When combined"
        "with linear feedback activation functions, this "
        "is similar to feedback alignment",
    )
    tgroup.add_argument(
        "--shallow_training",
        action="store_true",
        help="Train only the parameters of the last layer and" "let the others stay fixed.",
    )
    tgroup.add_argument(
        "--norm_ratio",
        type=float,
        default=1.0,
        help="hyperparameter used for computing the minimal "
        "norm update of the parameters, given the targets."
        "Default: %(default)s",
    )
    tgroup.add_argument(
        "--extra_fb_epochs",
        type=int,
        default=0,
        help="After each epoch of training, the fb parameters"
        "will be trained for an extra extra_fb_epochs "
        "epochs. Default: 0",
    )
    tgroup.add_argument(
        "--extra_fb_minibatches",
        type=int,
        default=0,
        help="After each minibatch training of the forward "
        "parameters, we do <N> extra minibatches training"
        "for the feedback weights. The extra minibatches "
        "are randomly sampled from the trainingset",
    )
    tgroup.add_argument(
        "--freeze_output_layer",
        action="store_true",
        help="Freeze the forward parameters of the output layer"
        "and only train the forward parameters of the "
        "hidden layers. The feedback parameters of all "
        "layers are still trained. ",
    )
    tgroup.add_argument(
        "--gn_damping_training",
        type=float,
        default=0.0,
        help="Thikonov damping used to train the GN network.",
    )
    tgroup.add_argument(
        "--not_randomized_fb",
        action="store_true",
        help="Depreciated argument. "
        "This flag applies for networks that use the "
        "difference reconstruction loss. The flag "
        "indicates that for each minibatch, all feedback "
        "parameters should be trained instead of only "
        "one set of randomly drawn feedback parameters.",
    )
    tgroup.add_argument(
        "--train_randomized_fb",
        action="store_true",
        help="This flag applies for networks that use the "
        "difference reconstruction loss. The flag "
        "indicates that for each minibatch, one layer is "
        "selected randomly for training the feedback "
        "parameters.",
    )
    tgroup.add_argument(
        "--only_train_first_layer",
        action="store_true",
        help="Only train the forward parameters of the first "
        "layer, while freezing all other forward"
        " parameters to their initialization. The feedback"
        "parameters are all trained.",
    )
    tgroup.add_argument(
        "--no_val_set",
        action="store_true",
        help="Flag indicating that no validation set is used" "during training.",
    )
    tgroup.add_argument(
        "--no_preprocessing_mnist",
        action="store_true",
        help="take the mnist input values between 0 and 1, " "instead of standardizing them.",
    )
    tgroup.add_argument(
        "--loss_scale",
        type=float,
        default=1.0,
        help="Depreciated. " "Scale the loss by this factor to mitigate " "numerical problems.",
    )
    tgroup.add_argument(
        "--only_train_last_two_layers",
        action="store_true",
        help="Only train the last two layers of the " "network.",
    )
    tgroup.add_argument(
        "--only_train_last_three_layers",
        action="store_true",
        help="Only train the last three layers of the " "network.",
    )
    tgroup.add_argument(
        "--only_train_last_four_layers",
        action="store_true",
        help="Only train the last four layers of the " "network.",
    )

    agroup = parser.add_argument_group("Training options for the " "Adam optimizer")
    agroup.add_argument(
        "--beta1",
        type=float,
        default=0.99,
        help="beta1 training hyperparameter for the adam " "optimizer. Default: %(default)s",
    )
    agroup.add_argument(
        "--beta2",
        type=float,
        default=0.99,
        help="beta2 training hyperparameter for the adam " "optimizer. Default: %(default)s",
    )
    agroup.add_argument(
        "--epsilon",
        type=str,
        default="1e-4",
        help="epsilon training hyperparameter for the adam " "optimizer. Default: %(default)s",
    )
    agroup.add_argument(
        "--beta1_fb",
        type=float,
        default=0.99,
        help="beta1 training hyperparameter for the adam "
        "feedback optimizer. Default: %(default)s",
    )
    agroup.add_argument(
        "--beta2_fb",
        type=float,
        default=0.99,
        help="beta2 training hyperparameter for the adam "
        "feedback optimizer. Default: %(default)s",
    )
    agroup.add_argument(
        "--epsilon_fb",
        type=str,
        default="1e-4",
        help="epsilon training hyperparameter for the adam "
        "feedback optimizer. Default: %(default)s",
    )

    sgroup = parser.add_argument_group("Network options")
    sgroup.add_argument("--hidden_layers", type=int, nargs="+", default=None)
    # help='Number of hidden layer in the (student) ' +
    #      'network. Default: %(default)s.')
    sgroup.add_argument(
        "--num_hidden",
        type=int,
        metavar="N",
        default=2,
        help="Number of hidden layer in the " + "network. Default: %(default)s.",
    )
    sgroup.add_argument(
        "--size_hidden",
        type=str,
        metavar="N",
        default="500",
        help="Number of units in each hidden layer of the "
        + "(student) network. Default: %(default)s."
        "If you provide a list, you can have layers of "
        "different sizes.",
    )
    sgroup.add_argument(
        "--size_input",
        type=int,
        metavar="N",
        default=3072,
        help="Number of units of the input" ". Default: %(default)s.",
    )
    sgroup.add_argument(
        "--size_output",
        type=int,
        metavar="N",
        default=10,
        help="Number of units of the output" ". Default: %(default)s.",
    )
    sgroup.add_argument(
        "--size_hidden_fb",
        type=int,
        metavar="N",
        default=500,
        help="Number of units of the hidden feedback layer "
        "(in the DDTP-RHL variants)."
        ". Default: %(default)s.",
    )
    sgroup.add_argument(
        "--hidden_activation",
        type=str,
        default="tanh",
        choices=["tanh", "relu", "linear", "leakyrelu", "elu", "sigmoid"],
        help="Activation function used for the hidden layers. " "Default: $(default)s.",
    )
    sgroup.add_argument(
        "--output_activation",
        type=str,
        default="softmax",
        choices=["tanh", "relu", "linear", "leakyrelu", "elu", "sigmoid", "softmax"],
        help="Activation function used for the output. " "Default: $(default)s.",
    )
    sgroup.add_argument(
        "--fb_activation",
        type=str,
        default=None,
        choices=["tanh", "relu", "linear", "leakyrelu", "elu", "sigmoid"],
        help="Activation function used for the feedback targets"
        "for the hidden layers. Default the same as "
        "hidden_activation.",
    )
    sgroup.add_argument(
        "--no_bias", action="store_true", help="Flag for not using biases in the network."
    )
    sgroup.add_argument(
        "--network_type",
        type=str,
        default="DDTPConvCIFAR",
        choices=[
            "DTP",
            "LeeDTP",
            "DTPDR",
            "DKDTP2",
            "DMLPDTP2",
            "BP",
            "GN2",
            "DFA",
            "DDTPControl",
            "DDTPConv",
            "DFAConv",
            "BPConv",
            "DDTPConvCIFAR",
            "DFAConvCIFAR",
            "BPConvCIFAR",
            "DDTPConvControlCIFAR",
        ],
        help="Variant of TP that will be used to train the "
        "network. See the layer classes for explanations "
        "of the names. Default: %(default)s.",
    )
    sgroup.add_argument(
        "--initialization",
        type=str,
        default="xavier_normal",
        choices=["orthogonal", "xavier", "xavier_normal", "teacher"],
        help="Type of initialization that will be used for the "
        "forward and feedback weights of the network."
        "Default: %(default)s.",
    )
    sgroup.add_argument(
        "--size_mlp_fb",
        type=str,
        default="100",
        help="The size of the hidden layers of the MLP that is"
        "used in the DMLPDTP layers. For one hidden layer,"
        "provide the integer indicating the size of the "
        "hidden layer. For multiple hidden layers, provide"
        'a list with all layer sizes, separated by ",",'
        'without spaces and encapsulated by "[]". If you'
        "dont want any hidden layers, give None.",
    )
    sgroup.add_argument(
        "--hidden_fb_activation",
        type=str,
        default=None,
        choices=["tanh", "relu", "linear", "leakyrelu", "sigmoid"],
        help="Activation function used for the hidden layers of"
        "the direct feedback mapping. "
        "Default: $(default)s.",
    )
    sgroup.add_argument(
        "--recurrent_input",
        action="store_true",
        help="flag indicating whether the direct feedback "
        "mapping should also use the nonlinear activation"
        " of the current layer as input to improve the "
        "feedback mapping.",
    )

    mgroup = parser.add_argument_group("Miscellaneous options")
    mgroup.add_argument("--no_cuda", action="store_true", help="Flag to disable GPU usage.")
    mgroup.add_argument(
        "--random_seed",
        type=int,
        metavar="N",
        default=42,
        help="Random seed. Default: %(default)s.",
    )
    mgroup.add_argument(
        "--cuda_deterministic",
        action="store_true",
        help="Flag to make the GPU computations deterministic."
        "note: this slows down computation!",
    )
    mgroup.add_argument(
        "--freeze_BPlayers",
        action="store_true",
        help="Flag to freeze the parameters of the output "
        "layer and the last hidden layer, that normally "
        "are trained with BP in the LeeDTP network, "
        "to see if DTP transmits "
        "useful teaching signals.",
    )
    mgroup.add_argument(
        "--hpsearch",
        action="store_true",
        help="Flag indicating that the main script is running "
        "in the context of a hyper parameter search.",
    )
    mgroup.add_argument(
        "--multiple_hpsearch",
        action="store_true",
        help="flag indicating that main is runned in the " "context of multiple_hpsearches.py",
    )
    mgroup.add_argument(
        "--double_precision",
        action="store_true",
        help="use double precision floats (64bits) instead of "
        "32bit floats to increase the precision of the "
        "computations. This slows down training.",
    )
    mgroup.add_argument(
        "--evaluate",
        action="store_true",
        help="Don't stop unpromising runs, because we are " "evaluating hp parameter results.",
    )

    vgroup = parser.add_argument_group("Logging options")
    vgroup.add_argument(
        "--out_dir",
        type=str,
        default="logs",
        help="Relative path to directory where the logs are " "saved.",
    )
    vgroup.add_argument(
        "--save_logs",
        action="store_true",
        help="Flag to save logs and plots by using " "tensorboardX.",
    )
    vgroup.add_argument(
        "--save_BP_angle",
        action="store_true",
        help="Flag indicating whether the BP updates and the"
        "angle between those updates and the TP updates"
        "should be computed and saved.",
    )
    vgroup.add_argument(
        "--save_GN_angle",
        action="store_true",
        help="Flag indicating whether the GN updates and the"
        "angle between those updates and the TP updates"
        "should be computed and saved. Warning: this "
        "causes a heavy extra computational load.",
    )
    vgroup.add_argument(
        "--save_GNT_angle",
        action="store_true",
        help="Flag inidcating whether angle with the ideal "
        "GNT updates should be computed. Warning, this"
        "causes a heavy extra computational load.",
    )
    vgroup.add_argument(
        "--save_GN_activations_angle",
        action="store_true",
        help="Flag indicating whether the Gauss-Newton updates"
        " for the layer activations should be computed and"
        "the angle with the TP updates for the activations"
        " should be computed and saved. Warning: this "
        "causes a heavy extra computational load.",
    )
    vgroup.add_argument(
        "--save_BP_activations_angle",
        action="store_true",
        help="Flag indicating whether the BP updates"
        " for the layer activations should be computed and"
        "the angle with the TP updates for the activations"
        " should be computed and saved.",
    )
    vgroup.add_argument(
        "--plots",
        type=str,
        default="save",
        choices=[None, "save", "save_and_show", "compute"],
    )
    vgroup.add_argument(
        "--save_loss_plot",
        action="store_true",
        help="Save a plot of the test loss and the training " "loss.",
    )
    vgroup.add_argument(
        "--create_plots",
        action="store_true",
        help="Flag indicating whether the angles should be plotted and saved",
    )
    vgroup.add_argument(
        "--gn_damping",
        type=str,
        default="0.",
        help="Thikonov damping used for computing the "
        "Gauss-Newton updates that are used to compute"
        "the angles between the actual updates and the"
        "GN updates. Default: %(default)s.",
    )
    vgroup.add_argument(
        "--log_interval",
        type=int,
        default=None,
        help="Each <log_interval> batches, the batch results" "are logged to tensorboard.",
    )
    vgroup.add_argument(
        "--output_space_plot",
        action="store_true",
        help="Make a plot of the trajectory of the output in "
        "the output space accompagnied by loss contours.",
    )
    vgroup.add_argument(
        "--output_space_plot_layer_idx",
        type=int,
        default=None,
        help="layer index for making the output_space_plot.",
    )
    vgroup.add_argument(
        "--output_space_plot_bp",
        action="store_true",
        help="plot the output space update for a BP update.",
    )
    vgroup.add_argument("--save_weights", action="store_true")
    vgroup.add_argument("--load_weights", action="store_true")
    vgroup.add_argument(
        "--gn_damping_hpsearch",
        action="store_true",
        help="Flag indicating whether a small hpsearch should"
        "be performed to optimize the gn_damping constant"
        "with which the gnt angles are computed.",
    )
    vgroup.add_argument(
        "--save_nullspace_norm_ratio",
        action="store_true",
        help="Flag indicating whether the norm ratio between the"
        "nullspace components of the parameter updates and"
        "the updates themselves should be computed and "
        "saved.",
    )
    return parser


def postprocess_args(args: argparse.Namespace) -> argparse.Namespace:
    args.save_angle = (
        args.save_GN_activations_angle
        or args.save_BP_activations_angle
        or args.save_BP_angle
        or args.save_GN_angle
        or args.save_GNT_angle
    )
    print(args)

    ### Create summary log writer
    curdir = os.path.curdir
    if args.out_dir is None:
        out_dir = os.path.join(
            curdir,
            "logs",
        )
        args.out_dir = out_dir
    else:
        out_dir = os.path.join(curdir, args.out_dir)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    print("Logging at {}".format(out_dir))

    with open(os.path.join(out_dir, "args.txt"), "w") as f:
        json.dump(args.__dict__, f, indent=2)

    if args.dataset in ["mnist", "fashion_mnist", "cifar10"]:
        args.classification = True
    else:
        args.classification = False

    if args.dataset in ["student_teacher", "boston"]:
        args.regression = True
    else:
        args.regression = False

    # initializing command line arguments if None
    if args.output_activation is None:
        if args.classification:
            args.output_activation = "softmax"
        elif args.regression:
            args.output_activation = "linear"
        else:
            raise ValueError("Dataset {} is not supported.".format(args.dataset))

    if args.fb_activation is None:
        args.fb_activation = args.hidden_activation

    if args.hidden_fb_activation is None:
        args.hidden_fb_activation = args.hidden_activation

    if args.optimizer_fb is None:
        args.optimizer_fb = args.optimizer

    # Manipulating command line arguments if asked
    args.lr = utils.process_lr(args.lr)
    args.lr_fb = utils.process_lr(args.lr_fb)
    args.nb_feedback_iterations = utils.process_nb_feedback_iterations(args.nb_feedback_iterations)
    args.epsilon_fb = utils.process_lr(args.epsilon_fb)
    args.epsilon = utils.process_lr(args.epsilon)
    args.size_hidden = utils.process_hdim(args.size_hidden)
    args.random_seed = int(args.random_seed)
    if args.size_mlp_fb == "None":
        args.size_mlp_fb = None
    else:
        args.size_mlp_fb = utils.process_hdim_fb(args.size_mlp_fb)

    if args.normalize_lr:
        args.lr = args.lr / args.target_stepsize

    if args.network_type in ["GN", "GN2"]:
        # if the GN variant of the network is used, the fb weights do not need
        # to be trained
        args.freeze_fb_weights = True

    if args.network_type == "DFA":
        # manipulate cmd arguments such that we use a DMLPDTP2 network with
        # linear MLP's with fixed weights
        args.freeze_fb_weights = True
        args.network_type = "DMLPDTP2"
        args.size_mlp_fb = None
        args.fb_activation = "linear"
        args.train_randomized = False

    if args.network_type == "DFAConv":
        args.freeze_fb_weights = True
        args.network_type = "DDTPConv"
        args.fb_activation = "linear"
        args.train_randomized = False

    if args.network_type == "DFAConvCIFAR":
        args.freeze_fb_weights = True
        args.network_type = "DDTPConvCIFAR"
        args.fb_activation = "linear"
        args.train_randomized = False

    if args.network_type in ["DTPDR"]:
        args.diff_rec_loss = True
    else:
        args.diff_rec_loss = False

    if args.network_type in [
        "DKDTP",
        "DKDTP2",
        "DMLPDTP",
        "DMLPDTP2",
        "DDTPControl",
        "DDTPConv",
        "DDTPConvCIFAR",
        "DDTPConvControlCIFAR",
    ]:
        args.direct_fb = True
    else:
        args.direct_fb = False

    if isinstance(args.gn_damping, str) and "," in args.gn_damping:
        args.gn_damping = utils.str_to_list(args.gn_damping, type="float")
    else:
        args.gn_damping = float(args.gn_damping)

    # Checking valid combinations of command line arguments
    if args.shallow_training:
        if not args.network_type == "BP":
            raise ValueError(
                "The shallow_training method is only implemented"
                "in combination with BP. Make sure to set "
                "the network_type argument on BP."
            )
    return args


def launch(args: argparse.Namespace):

    ### Ensure deterministic computation.
    print(f"RANDOM SEED: {args.random_seed}")
    torch.manual_seed(int(args.random_seed))
    torch.cuda.manual_seed_all(int(args.random_seed))
    np.random.seed(int(args.random_seed))
    random.seed(int(args.random_seed))

    # Ensure that runs are reproducible even on GPU. Note, this slows down
    # training!
    # https://pytorch.org/docs/stable/notes/randomness.html
    if args.cuda_deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    use_cuda = (not args.no_cuda) and torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    if use_cuda:
        torch.set_default_tensor_type("torch.cuda.FloatTensor")
    print("Using cuda: " + str(use_cuda))

    if args.double_precision:
        torch.set_default_dtype(torch.float64)

    ### Create dataloaders

    if args.dataset == "mnist":
        # TODO: try different datanormalizations (e.g. between -1 and 1)
        print("### Training on MNIST ###")
        if args.multiple_hpsearch:
            data_dir = "../../../../../data"
        elif args.hpsearch:
            data_dir = "../../../../data"
        else:
            data_dir = "./data"

        if args.no_preprocessing_mnist:
            transform = transforms.Compose([transforms.ToTensor()])
        else:
            transform = transforms.Compose(
                [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
            )
        trainset_total = torchvision.datasets.MNIST(
            root=data_dir, train=True, download=True, transform=transform
        )

        if args.no_val_set:
            train_loader = torch.utils.data.DataLoader(
                trainset_total, batch_size=args.batch_size, shuffle=True, num_workers=0
            )
            val_loader = None
        else:
            trainset, valset = torch.utils.data.random_split(trainset_total, [55000, 5000])
            train_loader = torch.utils.data.DataLoader(
                trainset, batch_size=args.batch_size, shuffle=True, num_workers=0
            )
            val_loader = torch.utils.data.DataLoader(
                valset, batch_size=args.batch_size, shuffle=False, num_workers=0
            )
        testset = torchvision.datasets.MNIST(
            root=data_dir, train=False, download=True, transform=transform
        )
        test_loader = torch.utils.data.DataLoader(
            testset, batch_size=args.batch_size, shuffle=False, num_workers=0
        )

    elif args.dataset == "fashion_mnist":
        print("### Training on Fashion-MNIST ###")
        if args.multiple_hpsearch:
            data_dir = "../../../../../data"
        elif args.hpsearch:
            data_dir = "../../../../data"
        else:
            data_dir = "./data"
        transform = transforms.Compose([transforms.ToTensor()])
        trainset_total = torchvision.datasets.FashionMNIST(
            root=data_dir, train=True, download=True, transform=transform
        )

        if args.no_val_set:
            train_loader = torch.utils.data.DataLoader(
                trainset_total, batch_size=args.batch_size, shuffle=True, num_workers=0
            )
            val_loader = None
        else:
            trainset, valset = torch.utils.data.random_split(trainset_total, [55000, 5000])
            train_loader = torch.utils.data.DataLoader(
                trainset, batch_size=args.batch_size, shuffle=True, num_workers=0
            )
            val_loader = torch.utils.data.DataLoader(
                valset, batch_size=args.batch_size, shuffle=False, num_workers=0
            )
        testset = torchvision.datasets.FashionMNIST(
            root=data_dir, train=False, download=True, transform=transform
        )
        test_loader = torch.utils.data.DataLoader(
            testset, batch_size=args.batch_size, shuffle=False, num_workers=0
        )

    elif args.dataset == "cifar10":
        print("### Training on CIFAR10")
        if args.multiple_hpsearch:
            data_dir = "../../../../../data"
        elif args.hpsearch:
            data_dir = "../../../../data"
        else:
            data_dir = "./data"

        transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    (0.4914, 0.4822, 0.4465), (3 * 0.2023, 3 * 0.1994, 3 * 0.2010)
                ),
            ]
        )

        trainset_total = torchvision.datasets.CIFAR10(
            root=data_dir, train=True, download=True, transform=transform
        )
        if args.no_val_set:
            train_loader = torch.utils.data.DataLoader(
                trainset_total, batch_size=args.batch_size, shuffle=True, num_workers=0
            )
            val_loader = None
        else:
            g_cuda = torch.Generator(device="cuda")
            from torch.utils.data import random_split, DataLoader

            trainset, valset = random_split(trainset_total, [45000, 5000], generator=g_cuda)
            train_loader = torch.utils.data.DataLoader(
                trainset, batch_size=args.batch_size, shuffle=True, num_workers=0, generator=g_cuda
            )
            val_loader = torch.utils.data.DataLoader(
                valset, batch_size=args.batch_size, shuffle=False, num_workers=0, generator=g_cuda
            )
        testset = torchvision.datasets.CIFAR10(
            root=data_dir, train=False, download=True, transform=transform
        )
        test_loader = torch.utils.data.DataLoader(
            testset, batch_size=args.batch_size, shuffle=False, num_workers=0
        )

    elif args.dataset == "student_teacher":
        print("### Training a student_teacher regression model ###")
        train_x, test_x, val_x, train_y, test_y, val_y = builders.generate_data_from_teacher(
            n_in=args.size_input,
            n_out=args.size_output,
            n_hidden=[1000, 1000, 1000, 1000],
            device=device,
            num_train=args.num_train,
            num_test=args.num_test,
            num_val=args.num_val,
            args=args,
            activation="relu",
        )

        train_loader = DataLoader(
            utils.RegressionDataset(train_x, train_y, args.double_precision),
            batch_size=args.batch_size,
            shuffle=True,
        )
        test_loader = DataLoader(
            utils.RegressionDataset(test_x, test_y, args.double_precision),
            batch_size=args.batch_size,
            shuffle=False,
        )
        if args.no_val_set:
            val_loader = None
        else:
            val_loader = DataLoader(
                utils.RegressionDataset(val_x, val_y, args.double_precision),
                batch_size=args.batch_size,
                shuffle=False,
            )

    else:
        raise ValueError("The provided dataset {} is not supported.".format(args.dataset))

    if args.log_interval is None:
        args.log_interval = max(1, int(len(train_loader) / 100))
        # 100 logpoint per epoch

    if args.save_logs:
        writer = SummaryWriter(logdir=out_dir)
    else:
        writer = None

    ### Initialize summary file
    summary = utils.setup_summary_dict(args)

    ### Generate network
    net = builders.build_network(args)

    ### Train network
    print("train")
    import time

    start_time = time.time()

    if not args.network_type in ("BP", "BPConv"):
        summary = train(
            args=args,
            device=device,
            train_loader=train_loader,
            net=net,
            writer=writer,
            test_loader=test_loader,
            summary=summary,
            val_loader=val_loader,
        )
    else:
        summary = train_bp(
            args=args,
            device=device,
            train_loader=train_loader,
            net=net,
            writer=writer,
            test_loader=test_loader,
            summary=summary,
            val_loader=val_loader,
        )

    training_time = time.time() - start_time
    # if (args.plots is not None and args.network_type != 'BP'):
    if args.network_type != "BP":
        summary["bp_activation_angles"] = net.bp_activation_angles
        summary["gn_activation_angles"] = net.gn_activation_angles
        summary["bp_angles"] = net.bp_angles
        summary["gnt_angles"] = net.gnt_angles
        summary["bp_activation_distances"] = net.bp_activation_distances
        summary["gn_activation_distances"] = net.gn_activation_distances
        summary["bp_distances"] = net.bp_distances
        summary["gnt_distances"] = net.gnt_distances
        # summary['nullspace_relative_norm_angles'] = net.nullspace_relative_norm

    # write final summary
    if summary["finished"] == 0:
        # if no error code in finished, put it on 1 to indicate succesful run
        summary["finished"] = 1
        summary["training_time"] = training_time
        utils.save_summary_dict(args, summary)
    if writer is not None:
        writer.close()

    if args.save_loss_plot:
        utils.plot_loss(summary, logdir=args.out_dir, logplot=True)

    # dump the whole summary in a pickle file
    filename = os.path.join(args.out_dir, "results.pickle")
    with open(filename, "wb") as f:
        pickle.dump(summary, f)

    return summary


if __name__ == "__main__":
    # print(os.getcwd())
    run()
