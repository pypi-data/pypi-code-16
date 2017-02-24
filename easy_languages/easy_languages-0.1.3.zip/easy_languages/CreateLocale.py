import os
def setup():
    if 'locales' not in os.listdir('.'): os.mkdir('locales')
    open('locales/config.ini', 'w', encoding='UTF-8').write('''[main]
default_language = en
language = en''')
setup()