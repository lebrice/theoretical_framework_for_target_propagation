config = {
'lr': 0.00038484282691424794,
'beta1': 0.9,
'beta2': 0.999,
'epsilon': 3.1339055831941025e-08,
'out_dir': 'logs/fashion_mnist/DFA',
'network_type': 'DFA',
'fb_activation': 'linear',
'initialization': 'xavier_normal',
'target_stepsize': 1.0,
'dataset': 'mnist',
'optimizer': 'Adam',
'optimizer_fb': 'Adam',
'momentum': 0.0,
'parallel': True,
'normalize_lr': True,
'batch_size': 128,
'forward_wd': 0.0,
'epochs_fb': 0,
'not_randomized': True,
'not_randomized_fb': True,
'extra_fb_minibatches': 0,
'extra_fb_epochs': 0,
'epochs': 100,
'only_train_first_layer': False,
'no_val_set': True,
'num_hidden': 5,
'size_hidden': 256,
'size_input': 784,
'size_output': 10,
'hidden_activation': 'tanh',
'output_activation': 'softmax',
'no_bias': False,
'no_cuda': False,
'random_seed': 42,
'cuda_deterministic': False,
'freeze_BPlayers': False,
'multiple_hpsearch': False,
'double_precision': True,
'save_logs': False,
'save_BP_angle': False,
'save_GN_angle': False,
'save_GN_activations_angle': False,
'save_BP_activations_angle': False,
'gn_damping': 0.0,
'hpsearch': False,
'log_interval': 80,
}