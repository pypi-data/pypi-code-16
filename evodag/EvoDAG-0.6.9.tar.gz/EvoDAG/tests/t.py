import numpy as np
from test_root import X, cl
from EvoDAG import EvoDAG
import logging
logging.basicConfig(level=logging.INFO)
y = cl.copy()
gp = EvoDAG(generations=np.inf,
            tournament_size=2,
            early_stopping_rounds=100,
            time_limit=0.9,
            multiple_outputs=True,
            seed=0,
            popsize=10000).fit(X, y)
