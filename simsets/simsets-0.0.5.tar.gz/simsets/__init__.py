from __future__ import print_function
import numpy
import pandas as pd

def simulate_dataset(dataframe, length = 100):
    simulated = dataframe[:0]
    for count in range(0,length):
        row = {}
        for variable, values in dataframe.items():
            row[variable]=numpy.random.choice(values)
        simulated.loc[count]= pd.Series(row)

    return simulated