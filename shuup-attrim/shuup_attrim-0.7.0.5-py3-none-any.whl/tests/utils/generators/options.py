from typing import List, Callable

from faker import Faker
from shuup_dev_testutils.generators import UniqueGenerator
from shuup_dev_testutils.generators.unique import GeneratedValue

from attrim.models.cls import OptionDict
from attrim.types import AttrimType
from shuup_dev_utils.settings import LANG_LIST


class OptionsGenerator:
    _fake = None
    _unique_generator = None

    def __init__(self):
        self._fake = Faker()
        self._unique_generator = UniqueGenerator()

    # noinspection PyShadowingBuiltins
    def list(
        self,
        type: AttrimType = AttrimType.trans_str,
        amount: int = 4,
    ) -> List[OptionDict]:
        if type is AttrimType.int:
            options = self._int_list(amount=amount)
        elif type is AttrimType.trans_str:
            options = self._trans_str_list(amount=amount)
        else:
            raise NotImplementedError(
                'Given type not implemented for options generator'
            )
        return options

    def _int_list(self, amount: int = 10) -> List[OptionDict]:
        options_list = self._simple_value_list(
            amount=amount,
            generator_fn=self._unique_generator.integer,
        )
        return options_list

    def _str_list(self, amount: int = 10) -> List[OptionDict]:
        options_list = self._simple_value_list(
            amount=amount,
            generator_fn=self._unique_generator.word,
        )
        return options_list

    def _simple_value_list(
        self,
        generator_fn: Callable[[], GeneratedValue],
        amount: int = 10,
    ) -> List[OptionDict]:
        options_list = []
        for option_number in range(0, amount):
            option = {}
            option.update({'order': option_number})
            option.update({'value': generator_fn()})
            options_list.append(option)
        return options_list

    def _trans_str_list(self, amount: int = 10) -> List[OptionDict]:
        option_list = []
        for option_number in range(0, amount):
            option = self._trans_str(order=option_number)
            option_list.append(option)
        return option_list

    def _trans_str(self, order: int = None) -> OptionDict:
        """
        example:
            {
                'order': 0,
                'values': {'en': 'en value', 'fr': 'fr value'}
            }
        """
        option_data = {}

        option_data.update({'order': order})

        option_values = {}
        for lang_code in LANG_LIST:
            option_value = self._unique_generator.word()
            option_values.update({lang_code: option_value})

        option_data.update({'values': option_values})

        return option_data
