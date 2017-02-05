import inspect
import os
import random

from .console import interact


class Kata:
    def run(self, seed=None):
        if seed is not None:
            random.seed(seed)

        environment = self.get_environment()
        target_str = self.get_target_str()

        target = eval(target_str, globals(), environment)

        print('Your target is:')
        print(target)
        print()

        for k, v in environment.items():
            print('>>> {} = {}'.format(k, v))

        if interact(environment, target):
            print()
            print('Well done')
            print()
            return True
        else:
            print()
            print('My solution is:')
            print('>>> {}'.format(target_str))
            print(target)
            print()
            return False

    def get_environment(self):
        return NotImplemented

    def get_target_str(self):
        return NotImplemented

    @classmethod
    def module_name(cls):
        path = inspect.getfile(cls)
        return os.path.splitext(os.path.basename(path))[0]
