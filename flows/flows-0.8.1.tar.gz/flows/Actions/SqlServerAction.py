# #!/usr/bin/env python

# '''
# SqlServerAction.py
# ----------------------

# Copyright 2016 Davide Mastromatteo
# License: Apache-2.0
# '''

# import pymssql
# from flows.Actions.Action import Action


# class SqlServerAction(Action):
#     """
#     SqlServerAction Class
#     """

#     type = "sqlserver"

#     conn = None
#     query = None
#     separator = ";"

#     def on_init(self):
#         super().on_init()

#         server = self.configuration['server']
#         user = self.configuration['user']
#         password = self.configuration['password']
#         dbname = self.configuration['dbname']

#         self.conn = pymssql.connect(
#             server, user, password, dbname)
#         self.query = self.configuration['query']
#         if 'separator' in self.configuration:
#             self.separator = self.configuration['separator']

#     def on_stop(self):
#         super().on_stop()
#         self.conn.close()

#     def on_input_received(self, action_input=None):
#         super().on_input_received(action_input)

#         # Action
#         if self.conn is not None and self.query is not None:
#             cursor = self.conn.cursor()
#             cursor.execute(self.query)

#             row = cursor.fetchone()
#             while row:
#                 return_value = self.separator.join(map(str, row))
#                 self.send_message(return_value)
#                 row = cursor.fetchone()
