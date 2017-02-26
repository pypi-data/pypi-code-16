import pandas as pd
import os


class vinegar:

    def __init__(self, path=None, dtype=str, overwrite=False):
        self.path = path
        assert os.path.isfile(self.path), self.path +' is not a file'
        self.dtype = dtype
        self.overwrite = overwrite
        self.df = self.logic()

    def logic(self):
        ''' csv path input(s) --> returns a pickle '''
            
        self.pkl = self.path.rsplit('.')[0] + '.pkl'
        # Return existing pickle if present and `overwrite` arg is false
        if os.path.isfile(self.pkl) and self.overwrite == False:
            print(self.pkl, "loaded from pickle")
        # Read csv into DataFrame and save pickle
        else:
            self.csv_pickle()
        return pd.read_pickle(self.pkl)

    def csv_pickle(self):
        csv = pd.read_csv(self.path, index_col=0, dtype=self.dtype, memory_map=True)
        csv = csv.reset_index(drop=False)
        csv.to_pickle(path=self.pkl)
        print(
            self.pkl,
            "saved to pickle",)


def pklr(**args):
    return vinegar(**args).df
