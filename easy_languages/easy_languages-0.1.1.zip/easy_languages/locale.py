import os
from configparser import ConfigParser

class locale():
    langs = {}

    fast_lang = ''

    def import_locales(self):


        for file in os.listdir("locales"):

            if file.endswith(".txt"):

                a = open('locales/'+file, encoding='UTF-8').read().split('\n')

                if len(a) == '':
                    raise Exception('Incorrect syntax in {}'.format(file))



                keys = {}

                for i in range(len(a)):
                    splited = a[i].split('==')


                    if len(splited) != 2:
                        raise Exception('Incorrect syntax in {}'.format(file))

                    keys.update({splited[0]: splited[1]})
                self.langs.update({file.replace('.txt', ''):keys})

    def fast_translate(self, key):
        if self.langs == {}:
            raise Exception('Locales is not defined')
        parser = ConfigParser()

        if 'config.ini' not in os.listdir('locales'): raise Exception('config.ini does not exist')
        parser.read('locales/config.ini')
        lang = parser.get('main', 'language')
        if lang not in self.langs: raise Exception('"{}" locale does not exist'.format(lang))
        if key not in self.langs[lang]: raise Exception('key "{0}" not in {1}'.format(key, lang))
        return self.langs[lang][key]

    def df_translate(self, key):
        if self.langs == {}:
            raise Exception('Locales is not defined')
        parser = ConfigParser()

        if 'config.ini' not in os.listdir('locales'): raise Exception('config.ini does not exist')
        parser.read('locales/config.ini')
        lang = parser.get('main', 'default_language')
        if lang not in self.langs: raise Exception('"{}" locale does not exist'.format(lang))
        if key not in self.langs[lang]: raise Exception('key "{0}" not in {1}'.format(key, lang))
        return self.langs[lang][key]

    def translate(self, key, lang):
        if self.langs == {}:
            raise Exception('Locales is not defined')

        if lang not in self.langs: raise Exception('"{}" locale does not exist'.format(lang))
        if key not in self.langs[lang]: raise Exception('key "{0}" not in {1}'.format(key, lang))
        return self.langs[lang][key]







