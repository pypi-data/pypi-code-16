#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from .twitter import Twitter
from .config import logged, file_exist, get_home_path


__author__ = "LaBatata (Victor Hugo Gomes Nascimento)"
__version__ = "0.3.20"
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

ui = '''
Name: {name}    Tweets: {statuses_count}    Curtidas: {favourites_count}
Seguindo: {friends_count}    Seguidores: {followers_count}

[1] Twittar    [2] Twittar Foto    [3] Twittar Video    [4] Timeline
[5] Pesquisar  [6] Home            [7] Direct Msg       [0] Sair

'''

twitter = Twitter()


def ui():
    user_info = twitter.get_user_information()
    print(LOGO + ui.format(name=user_info['name'],
                           statuses_count=user_info['tweets'],
                           favourites_count=user_info['fav'],
                           friends_count=user_info['following'],
                           followers_count=user_info['followers']))
    user_in = input('[@{screen_name}]: '.format(
                                        screen_name=user_info['screen_name']))
    return user_in


def log_on(twitter):
    if not file_exist(get_home_path() + '/.conf'):
        twitter.cria_conta()
    else:
        twitter.loga()
        logged(logged=True)


def main():
    global twitter
    log_on(twitter)

    while True:

        op = ui()
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
        elif op == '6':
            twitter.get_home_timeline()
        elif op == '7':
            twitter.send_direct_msg()
        else:
            print("Opção invalida!!")


if __name__ == '__main__':
    main()
