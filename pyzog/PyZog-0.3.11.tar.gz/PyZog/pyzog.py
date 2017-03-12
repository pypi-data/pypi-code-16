#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyZog.twitter import Twitter
from PyZog.config import logged, file_exist, get_home_path


__author__ = "LaBatata (victor hugo gomes)"
__version__ = "0.3.11"
__email__ = "labatata101@gmail.com"

LOGO = '''
                  ....
   ';.         .coooooo:::'
   :ooc'.     .ooooooooool,
   .loooooc;,';oooooooooo.  ____        _____
   ;coooooooooooooooooool  |  _ \ _   _|__  /___   __ _
    :ooooooooooooooooooo'  | |_) | | | | / // _ \ / _` |
     ,coooooooooooooooo;   |  __/| |_| |/ /| (_) | (_| |
      ;loooooooooooool'    |_|    \__, /____\___/ \__, |
        'loooooooool'             |___/           |___/
   .,clooooooool:,.
       .......                                 by @LaBatata101
'''

op = '''
[1] Twittar  [2] Twittar Foto  [3] Twittar Video  [4] Timeline
[5] Pesquisar                                     [0] Sair

'''


def ui():
    print(LOGO + op)


def log_on(twitter):
    if not file_exist(get_home_path() + '/.conf'):
        twitter.cria_conta()
    else:
        twitter.loga()
        logged(logged=True)


def main():
    twitter = Twitter()
    log_on(twitter)

    while True:

        ui()
        op = input('=> ')
        if op == '0':
            break
        elif op == '1':
            twitter.tweetar()
        elif op == '2':
            twitter.tweetar_com_foto()
        elif op == '3':
            twitter.tweetar_com_video()
        elif op == '4':
            twitter.timeline()
        elif op == '5':
            twitter.search()
        else:
            print("Opção invalida!!")


if __name__ == '__main__':
    main()
