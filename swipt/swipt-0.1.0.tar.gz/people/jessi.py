#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
jessi.py

Script that probably do something in python (in an efficient way or not... who knows it :P)
(As you can see I have not forgotten to add documentation)

Created by Jessica Fernandez on 2017-03
'''
import time


class Jessi(object):
    """ Class that may makes you smile :) """

    def __init__(self, *args, **kwargs):
        """ Initializes the most important attributes """
        self.leg_list = ('a_leg', 'r_leg', 'b_leg')
        self.madrid_to_berlin_call = {
            'a_leg': (0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 4, 0, 5, 0),
            'r_leg': (0, 0, 0, 1, 2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            'b_leg': (0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 4, 0, 5, 0, 0),
        }
        self.method_dict = {
            'default': ('INVITE', '100', '180', '408', 'ACK'),
            'r_leg': ('INVITE', '100', '302', 'ACK'),
        }

    def generate_flow_sip(self):
        """ Generates an unanswered flow sip from Madrid to Berlin (it looks like somebody is very busy there... :P) """
        print 'Jessi {0} Teles {0} Redir. {0} Pedro'.format(' '*16)
        num_packages = len(self.madrid_to_berlin_call['a_leg'])
        for num in range(num_packages):
            message = '  |'
            for leg in self.leg_list:
                methods = self.method_dict.get(leg, self.method_dict['default'])
                pos = self.madrid_to_berlin_call[leg][num]
                if not(leg == 'r_leg' and self.madrid_to_berlin_call['b_leg'][num]):
                    if pos:
                        method = methods[pos-1]
                        separator = '-'
                    else:
                        method = ''
                        separator = ' '
                    # It might be interesting to document the code below
                    if leg == 'b_leg' and pos:
                        # B Leg is larger than A or Redirect Legs, so separator should appear more times
                        num1 = 10*2 + 2 - int(round(len(method)/2.0, 0))
                        num2 = 10*2 + 1 - len(method)/2
                    else:
                        num1 = 10 - int(round(len(method)/2.0, 0))
                        num2 = 10 - len(method)/2
                    message += '{0} {1} {2}|'.format(separator*num1, method, separator*num2)
            print message
            if num not in (0, num_packages-2):
                time.sleep(1)
        print ''

    def show_message(self):
        """ Shows a farewell message """
        messages = (
            'Hola Pedro!!! Parece que no ha sido posible contactar contigo... jeje :P',
            'Que puedo decirte en este script...?',
            'Si es que despues de todo este tiempo trabajando en StoneWork contigo',
            'es imposible resumir aqui todo lo que he aprendido de ti.',
            'Podria enumerar muchas cosas, porque nos has hecho crecer como equipo en muchos sentidos,',
            'sin embargo, no solo nos has enseñado cosas como profesional, sino tambien como persona.',
            'Gracias por todo ello!!!',
            'Te vamos a echar mucho de menos por aqui!!! :-( Mucha suerte por Berlin!!! ^_^',
        )
        for message in messages:
            print message
            time.sleep(4)
        time.sleep(2)


def run():
    """ Just run functions """
    jessi = Jessi()
    jessi.generate_flow_sip()
    jessi.show_message()


run()
