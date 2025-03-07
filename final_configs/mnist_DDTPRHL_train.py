config = {
    "lr": 9.607871825148296e-05,
    "target_stepsize": 0.08650398125145677,
    "beta1": 0.9,
    "beta2": 0.9,
    "epsilon": 1.892605805264791e-08,
    "lr_fb": 0.0003264105195588272,
    "sigma": 0.003896077388858419,
    "feedback_wd": 0.000706049032042857,
    "beta1_fb": 0.999,
    "beta2_fb": 0.99,
    "epsilon_fb": 0.0002643993674792623,
    "out_dir": "logs/mnist/DKDTP2",
    "network_type": "DKDTP2",
    "recurrent_input": False,
    "hidden_fb_activation": "tanh",
    "fb_activation": "tanh",
    "initialization": "xavier_normal",
    "size_hidden_fb": 1024,
    "dataset": "mnist",
    "optimizer": "Adam",
    "optimizer_fb": "Adam",
    "momentum": 0.0,
    "parallel": True,
    "normalize_lr": True,
    "batch_size": 128,
    "forward_wd": 0.0,
    "epochs_fb": 6,
    "not_randomized": True,
    "not_randomized_fb": True,
    "extra_fb_minibatches": 0,
    "extra_fb_epochs": 1,
    "epochs": 100,
    "only_train_first_layer": False,
    "train_only_feedback_parameters": False,
    "no_val_set": True,
    "num_hidden": 5,
    "size_hidden": 256,
    "size_input": 784,
    "size_output": 10,
    "hidden_activation": "tanh",
    "output_activation": "softmax",
    "no_bias": False,
    "no_cuda": False,
    "random_seed": 42,
    "cuda_deterministic": False,
    "freeze_BPlayers": False,
    "multiple_hpsearch": False,
    "double_precision": True,
    "save_logs": False,
    "save_BP_angle": False,
    "save_GN_angle": False,
    "save_GN_activations_angle": False,
    "save_BP_activations_angle": False,
    "gn_damping": 0.0,
    "hpsearch": False,
    "log_interval": 80,
}
