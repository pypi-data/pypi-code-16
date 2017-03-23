# -*- coding: utf-8 -*-

from yapsy.IPlugin import IPlugin
import textwrap


class Mejortorrent(IPlugin):

    def list(self, pattern):
        print textwrap.dedent("""\
            #####################################
            #   RESULTS FROM MEJORTORRENT.COM   #
            #####################################
            """)

###########################################################################
##                   PROXIMAS PARADAS PROGRAMADAS                        ##
###########################################################################
##                                                                       ##
##   NO hay ninguna parada programada proximanente.                      ##
##                                                                       ##
###########################################################################
