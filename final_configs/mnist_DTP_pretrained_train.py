config = {
    "lr": 1.5720944356943283e-05,
    "target_stepsize": 0.1323571252777585,
    "feedback_wd": 0.00023867380258470717,
    "beta1": 0.9,
    "beta2": 0.99,
    "epsilon": 1.292390947076662e-08,
    "lr_fb": 2.2960882450559396e-05,
    "sigma": 0.009185269864166859,
    "beta1_fb": 0.9,
    "beta2_fb": 0.9,
    "epsilon_fb": 1.2435425546063357e-08,
    "out_dir": "logs/mnist/DTP_improved",
    "network_type": "DTP",
    "initialization": "xavier_normal",
    "fb_activation": "tanh",
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
