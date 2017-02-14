#!/usr/bin/env python3
"""MaisBot.
Para mais detalhes digite 'mais help'

Usage:
    mais config
    mais marca        [<file>] [--text=<doc>] [--pasta=<folder>]

Options:
    <file>          Arquivo de imagem para a operação

"""
import json
from colorama import Fore, Style
from docopt import docopt
from imagebot import __version__
from imagebot.watermark import watermark_folder
from imagebot.config import get_config_data
from imagebot.utils import confirma


def main():
    arguments = docopt(__doc__, version=__version__)

    if arguments['config']:
        data = get_config_data()
        if data:
            print("Configuração Atual:")
            print(json.dumps(data, indent=2))
            resposta = confirma("Deseja rodar a configuração?")
            if resposta:
                data = get_config_data(
                    start_over=True
                )
        else:
            data = get_config_data()
        return True

    if arguments['marca']:
        ret = watermark_folder(
            text=arguments['--text'],
            folder=arguments['--pasta']
        )
        return ret


def start():
    print(Fore.GREEN + "\n***************************\n")
    print("MaisBot! v.{}\n".format(__version__))
    print("***************************")
    print(Style.RESET_ALL)
    ret = main()
    print('\nOperação concluída\n')


if __name__ == "__main__":
    start()
