config = {
    "lr": 0.0003814330192320173,
    "beta1": 0.9,
    "beta2": 0.999,
    "epsilon": 2.5157431832952267e-05,
    "out_dir": "logs/cifar10/DFA",
    "network_type": "DFA",
    "fb_activation": "linear",
    "initialization": "xavier_normal",
    "target_stepsize": 1.0,
    "dataset": "cifar10",
    "optimizer": "Adam",
    "optimizer_fb": "Adam",
    "momentum": 0.0,
    "parallel": True,
    "normalize_lr": True,
    "batch_size": 128,
    "forward_wd": 0.0,
    "epochs_fb": 0,
    "not_randomized": True,
    "not_randomized_fb": True,
    "extra_fb_minibatches": 0,
    "epochs": 100,
    "double_precision": True,
    "num_hidden": 3,
    "size_hidden": 1024,
    "size_input": 3072,
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
    "log_interval": 5,
}
