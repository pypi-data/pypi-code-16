import pickle
from unittest import TestCase
from nose import tools
from ddt import ddt
from ddt import data
from ..model import compute_T_score


with open('toy_data.pcl', 'r') as iofile:
    toy_data_dict = pickle.load(iofile)

def toy_results_are_equal(test_idx):
    estimated_T_score = compute_T_score(toy_data_dict['event_line_matrix'][test_idx],
                                        toy_data_dict['line_stream_matrix'][test_idx],
                                        toy_data_dict['prescale'][test_idx])
    return tools.assert_almost_equal(estimated_T_score, toy_data_dict['T_score_results'][test_idx])

@ddt
class TestCompute_T_score(TestCase):
    @data(0, 1, 2, 3)
    def test_trivial_case(self, test_idx):
        self.assertTrue(self, toy_results_are_equal(test_idx))

    def test_compute_T_score(self):
        pass

