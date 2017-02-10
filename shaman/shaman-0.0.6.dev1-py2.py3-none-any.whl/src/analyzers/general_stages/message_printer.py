from shaman.src.analyzers.abstract_stage import AbstractStage


class MessagePrinterStage(AbstractStage):
    """
    Prints a result from message.

    Input data:
        - filed names to print
    Output data:
        - None
    """
    def init_stage(self):
        self.message_fields_to_print = self.config['fields_to_print'].split(',')

    def do_stage(self, message):
        for field in self.message_fields_to_print:
            if field in message.__dict__:
                if not type(message.__dict__[field]) is dict:
                    if self.py_version == 2:
                        print('{} : {}'.format(field, message.__dict__[field]))
                    else:
                        print('{} : {}'.format(field, message.__dict__[field]))
                else:
                    print('{} : {}'.format(field, message.__dict__[field]))

        return message
