import os
import platform
from os.path import expanduser
from colorama import Fore, Style
from imagebot import settings
from imagebot.utils import confirma


def get_config_data(filename=settings.CONFIG_FILE, start_over=False):
    # Verifica se a configuracao existe
    # Caso nao exista perguntar
    config = settings.CONFIG_DICT
    basepath = expanduser("~")
    filepath = os.path.join(basepath, ".{}".format(filename))

    # Checa:
    # 1. arquivo de configuracao existe,
    # 2. arquivo está completo
    ret = True

    if not os.path.exists(filepath):
        ret = False
    else:
        with open(filepath, 'r') as file:
            for line in file:
                if "=" in line:
                    key = line.split("=")[0].lower()
                    value = line.split("=")[1].rstrip()
                    config[key] = value

        for key in config:
            if not config.get(key):
                ret = False

    if ret and not start_over:
        return config
    else:
        print(Fore.YELLOW + "\n>> Configuração")
        print("***************")
        print(Style.RESET_ALL)

        if not start_over:
            resp = confirma("Deseja configurar os dados")
        else:
            resp = True
        if resp:
            with open(filepath, 'w') as file:
                for key in config:
                    if config.get(key):
                        ask = "Informe {} [{}]: ".format(
                            key.upper(), config.get(key))
                    else:
                        ask = "Informe {}: ".format(key.upper())

                    resposta_ok = False
                    while not resposta_ok:
                        try:
                            value = str(input(ask))
                            if not value and config[key]:
                                file.write(
                                    "{}={}\n".format(
                                        key.upper(), config[key]))
                                resposta_ok = True
                            if value:
                                config[key] = value
                                file.write(
                                    "{}={}\n".format(
                                        key.upper(), value))
                                resposta_ok = True
                        except KeyboardInterrupt:
                            print("\nOperação interrompida")
                            return False
                        except:
                            print('erro')
                            pass

    print("\n\n\nConfiguração concluída.")
    return False
