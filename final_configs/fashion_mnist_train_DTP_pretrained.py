config = {
    "lr": 5.854740019006692e-06,
    "target_stepsize": 0.013343171296788602,
    "feedback_wd": 1.5905737448250066e-06,
    "beta1": 0.9,
    "beta2": 0.9,
    "epsilon": 6.097842781997323e-08,
    "lr_fb": 0.0007037459607549333,
    "sigma": 0.04212278453600074,
    "beta1_fb": 0.99,
    "beta2_fb": 0.999,
    "epsilon_fb": 2.9161738911931673e-07,
    "out_dir": "logs/fashion_mnist/DTP",
    "network_type": "DTP",
    "initialization": "xavier_normal",
    "fb_activation": "tanh",
    "no_val_set": True,
    "dataset": "fashion_mnist",
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
    "log_interval": 30,
    "gn_damping_hpsearch": False,
}
