config = {
'lr': 5.853923327337887e-05,
'target_stepsize': 0.06692785794345907,
'feedback_wd': 5.3955934972975846e-05,
'beta1': 0.9,
'beta2': 0.999,
'epsilon': 1.6241132477640457e-06,
'lr_fb': 4.780905626010856e-05,
'sigma': 0.006339078037135994,
'beta1_fb': 0.9,
'beta2_fb': 0.999,
'epsilon_fb': 3.041173245264719e-07,
'out_dir': 'logs/mnist/DMLPDTP2_linear',
'network_type': 'DMLPDTP2',
'recurrent_input': False,
'hidden_fb_activation': 'linear',
'size_mlp_fb': None,
'fb_activation': 'linear',
'initialization': 'xavier_normal',
'dataset': 'cifar10',
'double_precision': True,
'optimizer': 'Adam',
'optimizer_fb': 'Adam',
'momentum': 0.0,
'parallel': True,
'normalize_lr': True,
'batch_size': 128,
'forward_wd': 0.0,
'epochs_fb': 10,
'not_randomized': True,
'not_randomized_fb': True,
'extra_fb_minibatches': 0,
'extra_fb_epochs': 2,
'epochs': 100,
'num_hidden': 3,
'size_hidden': 1024,
'size_input': 3072,
'size_output': 10,
'hidden_activation': 'tanh',
'output_activation': 'softmax',
'no_bias': False,
'no_cuda': False,
'random_seed': 42,
'cuda_deterministic': False,
'freeze_BPlayers': False,
'multiple_hpsearch': False,
'save_logs': False,
'save_BP_angle': False,
'save_GN_angle': False,
'save_GN_activations_angle': False,
'save_BP_activations_angle': False,
'gn_damping': 0.0,
'hpsearch': False,
'log_interval': 5,
}