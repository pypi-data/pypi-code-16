from typing import List

from shuup.testing.factories import get_default_product_type
from faker import Faker
from shuup_dev_utils.settings import LANG_LIST
from shuup_dev_testutils.generators import UniqueGenerator

from attrim.models import Class
from attrim.interface import attrim
from attrim.tests.utils.generators.options import OptionsGenerator
from attrim.types import AttrimType
from attrim.models.cls import OptionDict


class ClsGenerator:
    options = None

    _fake = None
    _unique_generator = None

    def __init__(self):
        self.options = OptionsGenerator()

        self._fake = Faker()
        self._unique_generator = UniqueGenerator()

    # noinspection PyShadowingBuiltins
    def model(
        self,
        code: str = None,
        name: dict = None,
        type: AttrimType = AttrimType.trans_str,
        options: List[OptionDict] = None,
        options_amount: int = 3,
    ) -> Class:
        cls = attrim.cls.create(
            code=code or self.code(),
            type=type,
            name=name or self.name(),
            product_type=get_default_product_type(),
        )

        if cls.is_int_type():
            cls.options = options or self.options.list(
                type=AttrimType.int,
                amount=options_amount,
            )
        elif cls.is_trans_str_type():
            cls.options = options or self.options.list(
                type=AttrimType.trans_str,
                amount=options_amount,
            )
        else:
            raise NotImplementedError(
                'Cls generator does not supports the given type yet'
            )

        cls.save()

        return cls

    def name(self) -> dict:
        name_dict = {}
        for lang_code in LANG_LIST:
            name_value_in_current_lang = self._fake.name()
            name_dict.update({lang_code: name_value_in_current_lang})
        return name_dict

    def code(self) -> str:
        return self._unique_generator.word()
