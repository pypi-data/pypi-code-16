'''
Get Duplicated parameter lists
'''
from collections import Counter
from .extension_base import ExtensionBase


DEFAULT_MIN_PARAM_COUNT = 5


class LizardExtension(ExtensionBase):
    FUNCTION_INFO = {
        "parameter_list_duplicates": {
            "caption": " dup_param_list ",
            "average_caption": " avg_dpl ",
            "regression": True},
        "parameter_list_duplicated_in_files": {
            "caption": " dup_param_list_f ",
            "average_caption": " avg_dpl_f ",
            "regression": True},
    }

    def __init__(self, context=None):
        self.all_count = Counter()
        self.all_count_per_file = Counter()
        super(LizardExtension, self).__init__(context)

    def reduce(self, fileinfo):
        flt = [
                f for f in fileinfo.function_list
                if len(f.parameters) >= DEFAULT_MIN_PARAM_COUNT
             ]
        self.all_count.update(self._parameters(f) for f in flt)
        self.all_count_per_file.update(set(self._parameters(f) for f in flt))
        for flist in fileinfo.function_list:
            flist.parameter_list_duplicates = 0
            flist.parameter_list_duplicated_in_files = 0

    def reduce_again(self, fileinfo):
        for flist in fileinfo.function_list:
            flist.parameter_list_duplicates = self.all_count[
                self._parameters(flist)]
            flist.parameter_list_duplicated_in_files = \
                self.all_count_per_file[self._parameters(flist)]

    @staticmethod
    def _parameters(finfo):
        return ",".join(finfo.parameters)
