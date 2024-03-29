import sys
import argparse
import random


def sample(min, max):
    assert min <= max, 'Incorrect argument: %r > %r' % (min, max)
    return random.uniform(min, max)


def is_iterable(obj):
    '''
    Test if object is iterable using EAFP idiom (and not a string)
    :param obj: Iterable or other type of object
    :return: True if iterable
    '''
    if isinstance(obj, str):
        return False
    try:
        _ = iter(obj)
        return True
    except TypeError:
        return False


def is_float(obj):
    '''
    Test if object is a float using EAFP idiom
    :param obj: Float or other type of object
    :return: True if iterable
    '''
    try:
        float(obj)
        return True
    except ValueError:
        return False


def is_integer(obj):
    '''
    Test if object is a string representation of an int
    :param obj: Int in string representation or other type of object
    :return: True if int in string representation
    '''
    try:
        isinstance(obj, int) or obj.isdigit()
        return True
    except AttributeError:
        return False


def handle_arg(value, name):
    if value is None:
        return None
    elif not is_iterable(value):
        return value
    elif len(value) == 1:
        return value[0]
    elif len(value) == 2:
        return sample(float(value[0]), float(value[1]))
    else:
        raise ValueError('ERROR: %r must a single value or range of min max values.', name)


def extract_experiment_factors(argv):
    factors = []

    for arg in argv:
        if arg.startswith('-') and arg not in ['-repeat', '-output']:
            factors.append(arg[1:])

    return factors


def format_experiment_arg(param_name, param_val):
    if isinstance(param_val, bool):
        val = "True" if param_val else "False"
    elif is_integer(param_val):
        val = str(param_val)
    elif is_float(param_val):
        val = "{:.4f}".format(param_val)
    else:
        val = str(param_val)

    str_rep = '_' + param_name + '_' + val
    return str_rep


def create_experiment(args, experiment_factors):
    config = {}
    experiment_name = ''

    for param_name, param in args.__dict__.items():
        param_val = handle_arg(param, param_name)
        config[param_name] = param_val

        if param_name in experiment_factors:
            experiment_name += format_experiment_arg(param_name, param_val)

    experiment_name = experiment_name[1:] if experiment_name != '' else 'default'

    return config, experiment_name

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def start_experiments_generator():
    """
    :return: Generator that generates experiments according to arguments given to program. May also randomize values.
    """
    BATCH_SIZE = 32
    GAMMA = 0.99
    REPLAY_BUFFER_SIZE = 1000000
    LEARNING_STARTS = 50000
    LEARNING_FREQ = 4
    FRAME_HISTORY_LEN = 4
    TARGET_UPDATE_FREQ = 10000
    LEARNING_RATE = 0.00025
    ALPHA = 0.95
    EPS = 0.01
    MIN_EPS = 0.1
    OUTPUT_PATH = 'experiments'

    parser = argparse.ArgumentParser(description='Train DQN for playing Pong.\n' + \
                                                 'Set hyperparameters with single values or range to sample from.')
    parser.add_argument('-adv_model', metavar='ADVANCED_MODEL', nargs='?', type=str2bool,
                        default='False', help='Uses an advanced ConvNet model with LeakyReLU activations and dropout instead.')
    parser.add_argument('-repeat', metavar='AMOUNT', nargs='?', type=int,
                        default=1, help='Amount of times to repeat each experiment')
    parser.add_argument('-max_steps', metavar='STEPS', nargs=1, type=int,
                        default=40000000, help='Number of steps applied to each experiment. Defaults to 5 million.')
    parser.add_argument('-lr', metavar='LEARNING_RATE', nargs='+', type=float,
                        default=LEARNING_RATE, help='Learning rate value OR range: min max')
    parser.add_argument('-batch', metavar='BATCH_SIZE', nargs='+', type=int,
                        default=BATCH_SIZE, help='Batch size')
    parser.add_argument('-gamma', metavar='GAMMA', nargs='+', type=float,
                        default=GAMMA, help='Gamma Value for Bellman Equation Error')
    parser.add_argument('-replay_size', metavar='REPLAY_BUFFER_SIZE', nargs='+', type=int,
                        default=REPLAY_BUFFER_SIZE, help='Replay Buffer Size')
    parser.add_argument('-learning_start', metavar='LEARNING_RATE_STARTS_AT', nargs='+', type=int,
                        default=LEARNING_STARTS, help='Learning step in which the model learning starts')
    parser.add_argument('-learning_freq', metavar='STEPS_FREQ', nargs='+', type=int,
                        default=LEARNING_FREQ, help='Learning frequency: How often Q network is "taught" and updated')
    parser.add_argument('-frame_hist', metavar='FRAME_HISTORY_LEN', nargs='+', type=int,
                        default=FRAME_HISTORY_LEN, help='How many frames back in history each sample contains')
    parser.add_argument('-target_update_freq', metavar='STEPS_FREQ', nargs='+', type=int,
                        default=TARGET_UPDATE_FREQ, help='Learning frequency: How often Qtarget network is updated to Q')
    parser.add_argument('-alpha', metavar='ALPHA', nargs='+', type=float,
                        default=ALPHA, help='Hyperparameter for RMSProp optimizer: smoothing constant')
    parser.add_argument('-eps', metavar='EPS', nargs='+', type=float,
                        default=EPS, help='Hyperparameter for RMSProp optimizer: ' + \
                                          'term added to the denominator to improve numerical stability')
    parser.add_argument('-min_eps', metavar='MIN_EPS', nargs='+', type=float,
                        default=MIN_EPS, help='Hyperparameter for determing the minimal exploration rate.')
    parser.add_argument('-seed', metavar='SEED VALUE', nargs=1, type=int,
                        default=0, help='Seed value used for randomization')
    parser.add_argument('-game', metavar='GAME ID', nargs=1, type=int,
                        default=3, help='Game to choose from: \n' +
                                        '0: BeamRider\n' +
                                        '1: Breakout\n' +
                                        '2: Enduro\n' +
                                        '3: Pong\n' +
                                        '4: Qbert\n' +
                                        '5: SeaQuest\n' +
                                        '6: SpaceInvaders')
    parser.add_argument('-output', metavar='PATH', nargs=1,
                        default=OUTPUT_PATH, help='Output path for trained DQN models and experiments statistics')
    args = parser.parse_args()

    experiment_factors = extract_experiment_factors(sys.argv)

    for _ in range(args.repeat):
        yield create_experiment(args, experiment_factors)
