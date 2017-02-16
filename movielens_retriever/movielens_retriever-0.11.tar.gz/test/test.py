import unittest
from movielens_retriever.data import MoviLens

class TestMovielensDataRetrieverMethods(unittest.TestCase):

    def test_get_ds10K(self):

        retriver = MoviLens(dataset_type=MoviLens.DS10K, save_interaction_matrix=True)
        retriver.get_data()


    def test_get_ds20m(self):
        retriver = MoviLens(dataset_type=MoviLens.DS20M, save_interaction_matrix=True)
        retriver.get_data()

    def test_get_ds10K_binary(self):
        retriver = MoviLens(dataset_type=MoviLens.DS10K, threshold=4.0, save_interaction_matrix=True)
        retriver.get_data()

    def test_get_ds20m_binary(self):
        retriver = MoviLens(dataset_type=MoviLens.DS20M, threshold=4.0, save_interaction_matrix=True)
        retriver.get_data()


if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.join(__file__, "..")))
    unittest.main()

