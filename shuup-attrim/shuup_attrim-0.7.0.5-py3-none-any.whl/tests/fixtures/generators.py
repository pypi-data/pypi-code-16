from attrim.helpers import get_languages_list

from faker import Faker


class Generator:
    str_values_generated = []
    int_values_generated = []
    faker = None
    
    def __init__(self):
        self.faker = Faker()

    def code(self) -> str:
        return self.faker.word()

    def name(self) -> dict:
        name_dict = {}
        for lang_code in get_languages_list():
            name_dict.update({lang_code: self.faker.name()})
        return name_dict

    def trans_str_options(self) -> list:
        options_list = []
        for index in range(1, 10):
            option = self.trans_str_option(order=index)
            options_list.append(option)
        return options_list

    def unique_str(self) -> str:
        word = self.faker.word()
        while True:
            if word in self.str_values_generated:
                word = self.faker.word()
                continue
            else:
                break
        self.str_values_generated.append(word)
        return word

    def int_options(self) -> list:
        options_list = []
        for index in range(1, 9):
            option = {}
            option.update({'order': index})
            option.update({'value': self.faker.pyint()})
        return options_list

    def trans_str_option(self, order: int = None) -> dict:
        option = {}
        option.update({'order': order})
        option_values = {}
        for lang_code in get_languages_list():
            option_values.update({lang_code: self.unique_str()})
        option.update({'values': option_values})
        
        return option
