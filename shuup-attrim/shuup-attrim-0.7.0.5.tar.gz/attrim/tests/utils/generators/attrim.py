from shuup_dev_testutils.generators import ShuupModelsGenerator
from shuup_dev_testutils.generators import UniqueGenerator

from attrim.tests.utils.generators.cls import ClsGenerator


class AttrimGenerator(ShuupModelsGenerator):
    cls = None

    _unique_generator = None

    def __init__(self):
        super().__init__()

        self._unique_generator = UniqueGenerator()

        self.cls = ClsGenerator()
