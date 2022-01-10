config = {
    "lr": 4.642236759634694e-05,
    "target_stepsize": 0.08553905897894667,
    "feedback_wd": 8.137707468690146e-05,
    "beta1": 0.999,
    "beta2": 0.99,
    "epsilon": 1.0970452527148417e-07,
    "lr_fb": 9.993976073274085e-05,
    "sigma": 0.012237837901674018,
    "beta1_fb": 0.999,
    "beta2_fb": 0.999,
    "epsilon_fb": 5.650639108826411e-07,
    "out_dir": "logs/fashion_mnist/DTPDR_nonseq",
    "network_type": "DTPDR",
    "initialization": "xavier_normal",
    "fb_activation": "tanh",
    "dataset": "cifar10",
    "optimizer": "Adam",
    "optimizer_fb": "Adam",
    "momentum": 0.0,
    "parallel": True,
    "normalize_lr": True,
    "batch_size": 128,
    "forward_wd": 0.0,
    "epochs_fb": 10,
    "not_randomized": True,
    "not_randomized_fb": True,
    "extra_fb_minibatches": 0,
    "extra_fb_epochs": 2,
    "epochs": 100,
    "double_precision": True,
    "no_val_set": True,
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
    "log_interval": 80,
}
