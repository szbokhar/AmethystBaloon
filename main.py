import sys
import argh
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import ipdb

import util
import load_data
import sarsa_util
import display
from RL_Config import *


@argh.arg('points_file',
        help='File containing point cloud data as list of points')
@argh.arg('path_pat',
        help='Filename pattern for path file data (eg. data/qm_hc{0}_{1}.txt)')
@argh.arg('data_ids', help='List of data ids', nargs='+', type=int)
@argh.arg('config_dir', help='Config directory')
@argh.arg('-b', '--blocksize', help='Grid block size', default=0.5)
@argh.arg('-s', '--sigma', help='Path reward sigma', default=5000)
def plot_path_rewards(points_file, path_pat, data_ids, config_dir, **extra):
    "Run basic q-learning algorithm"
    rl_config = RL_Config()
    rl_config.set_parameters(
            blocksize=extra['blocksize'])
    rl_config.load_pointcloud(points_file)
    rl_config.load_action_files(config_dir)
    rl_config.load_path_data(path_pat, data_ids)
    rl_config.format_grid_and_paths()

    display.plot_path_reward(rl_config.path_NN, rl_config.voxel_grid, extra['sigma'])

    plt.show()

@argh.arg('points_file',
        help='File containing point cloud data as list of points')
@argh.arg('-b', '--blocksize', default=0.5, help='Side length of grid cube')
@argh.arg('-s', '--start', default=0, help='Z level to begin plot at')
@argh.arg('-m', '--max_div', default=8, help='Divide max by this')
def show_denseplot(points_file, **extra):
    "Generate and show pointclound density plot"

    rl_config = RL_Config()
    rl_config.set_parameters(blocksize=extra['blocksize'])
    rl_config.load_pointcloud(points_file)
    rl_config.format_grid_and_paths()

    display.show_grid(rl_config.voxel_grid, extra['start'], extra['max_div'])

    plt.show()

@argh.arg('points_file',
        help='File containing point cloud data as list of points')
@argh.arg('path_pat',
        help='Filename pattern for path file data (eg. data/qm_hc{0}_{1}.txt)')
@argh.arg('data_ids', help='List of data ids', nargs='+', type=int)
@argh.arg('-c', '--count', default=4000, help='Number of points to plot')
@argh.arg('-b', '--blocksize', default=0.5, help='Side length of grid cube')
def show_points_and_path(points_file, path_pat, data_ids, **extra):
    """
        Loads points and path data files and plots them
    """

    count = extra['count']
    rl_config = RL_Config()
    rl_config.set_parameters(blocksize=extra['blocksize'])
    rl_config.load_pointcloud(points_file)
    rl_config.load_path_data(path_pat, data_ids)
    rl_config.format_grid_and_paths()

    display.make_basic_plot(rl_config, 0, ['b-', 'r-', 'g-'], count)

    plt.show()


@argh.arg('points_file',
        help='File containing point cloud data as list of points')
@argh.arg('path_pat',
        help='Filename pattern for path file data (eg. data/qm_hc{0}_{1}.txt)')
@argh.arg('data_ids', help='List of data ids', nargs='+', type=int)
@argh.arg('config_dir', help='Config directory')
@argh.arg('-a', '--alpha', help='Learning rate', default=0.5)
@argh.arg('-g', '--gamma', help='Discount factor', default=0.5)
@argh.arg('-b', '--blocksize', help='Grid block size', default=0.5)
@argh.arg('-i', '--iter', help='Number of q-learning iterations', default=1000)
@argh.arg('-m', '--memory_size', help='Iteration sample size', default=200)
@argh.arg('--state_functions', help='Functions specification',
        default=['hc_only_make_sarsa_lists','hc_only_NN','hc_only_reward','hc_only_transition'], nargs='+', type=str)
def basic_qlearn(points_file, path_pat, data_ids, config_dir, **extra):
    "Run basic q-learning algorithm"
    num_iter = extra['iter']
    memory_size = extra['memory_size']
    training_paths = []
    training_labels = []

    rl_config = RL_Config()
    rl_config.set_parameters(
            alpha=extra['alpha'],
            gamma=extra['gamma'],
            blocksize=extra['blocksize'])
    rl_config.paths_to_SARSA = getattr(sarsa_util, extra['state_functions'][0])
    rl_config.make_path_NN = getattr(sarsa_util, extra['state_functions'][1])
    rl_config.reward_function = getattr(sarsa_util, extra['state_functions'][2])
    rl_config.transition_function = getattr(sarsa_util, extra['state_functions'][3])
    rl_config.load_pointcloud(points_file)
    rl_config.load_action_files(config_dir)
    rl_config.load_path_data(path_pat, data_ids)
    rl_config.format_grid_and_paths()
    rl_config.paths_to_SARSA(rl_config)

    Q, vals = util.do_qlearn(rl_config, num_iter, memory_size)
    display.show_value(np.log(Q*1000+1))
    display.plot_1D(vals)

    plt.show()

@argh.arg('points_file',
        help='File containing point cloud data as list of points')
@argh.arg('path_pat',
        help='Filename pattern for path file data (eg. data/qm_hc{0}_{1}.txt)')
@argh.arg('data_ids', help='List of data ids', nargs='+', type=int)
@argh.arg('config_dir', help='Config directory')
@argh.arg('-a', '--alpha', help='Learning rate', default=0.5)
@argh.arg('-g', '--gamma', help='Discount factor', default=0.5)
@argh.arg('-b', '--blocksize', help='Grid block size', default=0.5)
@argh.arg('-i', '--iter', help='Number of q-learning iterations', default=1000)
@argh.arg('-m', '--memory_size', help='Iteration sample size', default=200)
@argh.arg('-l', '--elength', help='Episode length ', default=500)
@argh.arg('-e', '--epsilon', help='epsilon greedy parameter', default=0.9)
@argh.arg('-s', '--sigma', help='Path reward sigma', default=5000)
@argh.arg('--start', default=0, help='Z level to begin plot at')
@argh.arg('--max_div', default=8, help='Divide max by this')
@argh.arg('--state_functions', help='Functions specification',
        default=['hc_only_make_sarsa_lists','hc_only_NN','hc_only_reward','hc_only_transition'], nargs='+', type=str)
@argh.arg('--explore_functions', help='Functions specification',
        default=['hc_only_reset','hc_only_explore_step'], nargs='+', type=str)
def explore_qlearn(points_file, path_pat, data_ids, config_dir, **extra):
    "Run basic q-learning algorithm"
    num_iter = extra['iter']
    memory_size = extra['memory_size']

    rl_config = RL_Config()
    rl_config.set_parameters(
            alpha=extra['alpha'],
            gamma=extra['gamma'],
            sigma=extra['sigma'],
            epsilon=extra['epsilon'],
            blocksize=extra['blocksize'])
    rl_config.paths_to_SARSA = getattr(sarsa_util, extra['state_functions'][0])
    rl_config.make_path_NN = getattr(sarsa_util, extra['state_functions'][1])
    rl_config.reward_function = getattr(sarsa_util, extra['state_functions'][2])
    rl_config.transition_function = getattr(sarsa_util, extra['state_functions'][3])
    rl_config.get_random_state = getattr(sarsa_util, extra['explore_functions'][0])
    rl_config.explore_step = getattr(sarsa_util, extra['explore_functions'][1])
    rl_config.load_pointcloud(points_file)
    rl_config.load_action_files(config_dir)
    rl_config.load_path_data(path_pat, data_ids)
    rl_config.format_grid_and_paths()
    rl_config.paths_to_SARSA(rl_config)

    (Q, vals, umap) = util.do_explore_qlearn(rl_config, num_iter=num_iter,
            rand_count=memory_size, reset_episode=extra['elength'])

    print('Density max: ', np.max(rl_config.voxel_grid))
    display.show_value(Q, 1)
    #display.show_value(umap, 20)
    display.plot_1D(vals)
    #display.plot_path_reward(rl_config.path_NN, rl_config.voxel_grid, extra['sigma'])
    display.show_grid(rl_config.voxel_grid, extra['start'], extra['max_div'])
    display.show_action_value(Q, 5, [0])
    display.show_action_value(Q, 6, [1])

    plt.show()


if __name__ == "__main__":
    np.set_printoptions(threshold=np.nan, linewidth=120)
    argh.dispatch_commands([show_points_and_path, basic_qlearn, show_denseplot,
            explore_qlearn, plot_path_rewards])
