config = {
    "lr": 8.882733337430332e-05,
    "target_stepsize": 0.09416689927228376,
    "beta1": 0.9,
    "beta2": 0.999,
    "epsilon": 5.552559684258553e-08,
    "lr_fb": 0.00018713096100900022,
    "sigma": 0.008719996683197298,
    "feedback_wd": 0.00040219548415666565,
    "beta1_fb": 0.9,
    "beta2_fb": 0.999,
    "epsilon_fb": 1.2297580110850507e-08,
    "out_dir": "logs/mnist/DDTPControl",
    "network_type": "DDTPControl",
    "recurrent_input": False,
    "hidden_fb_activation": "linear",
    "size_mlp_fb": None,
    "fb_activation": "linear",
    "initialization": "xavier_normal",
    "dataset": "mnist",
    "double_precision": True,
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
    "save_logs": False,
    "save_BP_angle": False,
    "save_GN_angle": False,
    "save_GN_activations_angle": False,
    "save_BP_activations_angle": False,
    "gn_damping": 0.0,
    "hpsearch": False,
    "log_interval": 50,
}
