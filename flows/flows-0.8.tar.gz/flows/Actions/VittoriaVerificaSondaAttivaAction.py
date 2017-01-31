#!/usr/bin/env python

'''
VittoriaVerificaSondaAttivaAction.py
------------------

Copyright 2016 Davide Mastromatteo
'''

from flows.Actions.Action import Action
import datetime


class VerificaSondaAttivaAction(Action):
    """
    VittoriaVerificaSondaAttivaAction Class
    """

    type = "VittoriaVerificaSondaAttiva"

    def on_init(self):
        super().on_init()

        str_date = datetime.date.strftime(datetime.date.today(), '%Y%m')
        self.filename = 'results' + str_date + '.csv'
        self.path = "\\\\vitt-web1.vittoriaassicurazioni.it\\FTPAGE\\ftpcloudmclink\\"

        if "path" in self.configuration:
            self.path = self.configuration["path"]
            if self.path[:-1] != "\\":
                self.path = self.path + "\\"

    def on_input_received(self, action_input=None):
        super().on_input_received(action_input)

        if action_input.sender == self.name:
            return None

        # Action
        return_value = None

        # do stuff...
        try:
            input_file = open(self.path + self.filename)

            sistemi = []
            last_esito = {}
            last_check_datetime = {}

            for line in input_file:

                tmp_last_sistema = ""
                tmp_last_esito = ""
                tmp_last_datetime = ""

                try:
                    last_check_date_string = line.split(',')[0]
                    tmp_last_sistema = line.split(',')[1]
                    tmp_last_esito = line.split(',')[2]
                    tmp_last_datetime = datetime.datetime.strptime(
                        last_check_date_string, '%Y-%m-%d %H:%M:%S.%f')
                except Exception:
                    continue

                if tmp_last_sistema not in sistemi:
                    sistemi.append(tmp_last_sistema)

                last_esito[tmp_last_sistema] = tmp_last_esito
                last_check_datetime[tmp_last_sistema] = tmp_last_datetime

            for sistema in sistemi:
                if abs(last_check_datetime[sistema] - datetime.datetime.now()).total_seconds() > 600:
                    return_value = (return_value or "") + \
                        "* Sonda attiva apparentemente bloccata per il sistema " + sistema + "\n"
                if last_esito[sistema] == 'ko':
                    return_value = (return_value or "") + \
                        "* L'ultima rilevazione della sonda attiva (" + str(last_check_datetime[sistema]) + ") riporta impossibilità di accedere al sistema " + sistema + "\n"

        except FileNotFoundError:
            return_value = "Il file di risultati della sonda attiva non è stato trovato"

        # returns the output
        self.send_message(return_value)
