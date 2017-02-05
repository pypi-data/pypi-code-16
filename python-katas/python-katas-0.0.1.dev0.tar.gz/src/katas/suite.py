import random

from .kata import Kata


class Suite:
    def __init__(self, katas):
        self.katas = katas

    def run(self):
        score = 0
        target = 3 * len(self.katas)
        scores = {kata: 3 for kata in self.katas}

        while True:
            kata = random.choice(list(scores.keys()))
            seed = random.randrange(100)

            print('-' * 80)
            print('{}::{}::{}'.format(kata.module_name(), type(kata).__name__, seed))
            print('Score: {} / {}'.format(score, target))
            print()

            if kata.run(seed):
                scores[kata] -= 1
                if scores[kata] == 0:
                    del scores[kata]
                score += 1
            else:
                scores[kata] += 1
                score -= 1

            if score == target:
                assert len(scores) == 0
                break

    @classmethod
    def from_module(cls, module):
        katas = [v() for k, v in vars(module).items() if isinstance(v, type) and issubclass(v, Kata) and k != 'Kata']
        return cls(katas)


    @classmethod
    def from_class(cls, kata_class):
        return cls([kata_class()])
