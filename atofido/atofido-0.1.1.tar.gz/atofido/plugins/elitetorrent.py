# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin
import textwrap


class Elitetorrent(IPlugin):

    def list(self, pattern):
        print textwrap.dedent("""\
            #####################################
            #   RESULTS FROM ELITETORRENT.NET   #
            #####################################
            """)

###########################################################################
##                   PROXIMAS PARADAS PROGRAMADAS                        ##
###########################################################################
##                                                                       ##
##   NO hay ninguna parada programada proximanente.                      ##
##                                                                       ##
###########################################################################