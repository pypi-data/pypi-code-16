import os.path as osp
import os


def log_args(func):
    """Log configurations of the experiment.
    """

    def wrapper(*args, **kwargs):
        if 'outdir' not in kwargs or 'gpu' not in kwargs:
            raise ValueError(
                'You need to declare directory of output with arg '
                '``outdir`` and ``gpu`` in order to visualize them with ilv')
        if len(args) > 0:
            raise ValueError('do not use positional arguments')
        if not osp.exists(kwargs['outdir']):
            os.makedirs(kwargs['outdir'])
        with open(osp.join(kwargs['outdir'], 'args'), 'w') as f:
            f.write(str(kwargs))

        func(*args, **kwargs)

    return wrapper
