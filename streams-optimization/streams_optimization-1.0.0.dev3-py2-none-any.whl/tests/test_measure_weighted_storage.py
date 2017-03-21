import pickle
from unittest import TestCase
from nose import tools
from ddt import ddt
from ddt import data
from ..utils import measure_weighted_storage


with open('toy_data.pcl', 'r') as iofile:
    toy_data_dict = pickle.load(iofile)

def toy_results_are_equal(test_idx):
    measured_storage_per_stream = measure_weighted_storage(toy_data_dict['event_line_matrix'][test_idx],
                                                           toy_data_dict['line_stream_matrix'][test_idx],
                                                           toy_data_dict['line_num_dict'],
                                                           toy_data_dict['dict_of_params'],
                                                           toy_data_dict['prescale'][test_idx])
    return tools.assert_almost_equals(measured_storage_per_stream, toy_data_dict['S_score_results'][test_idx])

@ddt
class TestMeasure_weighted_storage(TestCase):
    @data(0,1,2,3)
    def test_trivial_case(self, test_idx):
        self.assertTrue(self, toy_results_are_equal(test_idx))

    def test_measure_weighted_storage(self):
        pass