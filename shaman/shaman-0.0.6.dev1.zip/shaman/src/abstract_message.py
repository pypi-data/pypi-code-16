class MessageFormat:
    DATA = 0
    CONTROL = 1

control_messages = {'shutdown':'<SHUTDOWN_ALL_STAGES>'}
control_messages_invert_dict = {v:k for k,v in control_messages.items()}

class Message:
    """
    This class used to accumulate results and objects from every stage
    """
    def __init__(self):
        self.results = dict()
        self.format = MessageFormat.DATA
        self._fields_to_remove = list()
        self._correct_fields = list(self.__dict__.keys())+['_correct_fields']


    def add_result_to_message(self, result_name, result, result_storage_name):
        if result_storage_name not in self.results:
            self.results[result_storage_name] = dict()

        self.results[result_storage_name][result_name] = result
        return self

    def add_result_to_message_extra(self, result_name, result, result_storage_name):
        if result_storage_name not in self.results:
            self.results[result_storage_name] = dict()

        if 'extra' not in self.results[result_storage_name]:
            self.results[result_storage_name]['extra'] = dict()
                
        self.results[result_storage_name]['extra'][result_name] = result

    def add_result_to_message_extra_models(self, result_name, result, result_storage_name):
        if result_storage_name not in self.results:
            self.results[result_storage_name] = dict()

        if 'extra' not in self.results[result_storage_name]:
            self.results[result_storage_name]['extra'] = dict()
            self.results[result_storage_name]['extra']['models'] = dict()
                
        self.results[result_storage_name]['extra']['models'][result_name] = result

    def clean_fields(self):
        for f in self.__dict__:
            if f not in self._correct_fields:
                self._fields_to_remove.append(f)

        for f in self._fields_to_remove:
            self.__dict__.pop(f, None)

        self._fields_to_remove[:] = []

        for f in self.results:
            self._fields_to_remove.append(f)

        for f in self._fields_to_remove:
            self.results.pop(f, None)

        return self
