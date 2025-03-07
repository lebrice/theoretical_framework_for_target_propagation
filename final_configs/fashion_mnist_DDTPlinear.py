config = {
    "lr": 8.703567590317672e-06,
    "target_stepsize": 0.017250397502053975,
    "beta1": 0.99,
    "beta2": 0.99,
    "epsilon": 1.727973356862063e-08,
    "lr_fb": 0.0007959054461775743,
    "sigma": 0.09857259200102354,
    "feedback_wd": 5.782689838884453e-06,
    "beta1_fb": 0.99,
    "beta2_fb": 0.9,
    "epsilon_fb": 3.1081662356907766e-08,
    "out_dir": "logs/mnist/DMLPDTP2_linear",
    "network_type": "DMLPDTP2",
    "recurrent_input": False,
    "hidden_fb_activation": "linear",
    "size_mlp_fb": None,
    "fb_activation": "linear",
    "initialization": "xavier_normal",
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
    "save_GNT_angle": False,
    "save_GN_activations_angle": False,
    "save_BP_activations_angle": False,
    "gn_damping": 0,
    "hpsearch": False,
    "log_interval": 30,
    "gn_damping_hpsearch": False,
}
