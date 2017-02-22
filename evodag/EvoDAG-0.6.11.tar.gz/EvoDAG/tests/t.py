from EvoDAG.command_line import CommandLineParams
from EvoDAG import EvoDAG
from EvoDAG.utils import RandomParameterSearch, PARAMS
from tqdm import tqdm


class Evo(EvoDAG):
    pass


class A:
    pass


c = CommandLineParams()
c.data = A()
c.data.json = True
c.data.training_set = 'E.aa.json'
c.read_training_set()
rs = RandomParameterSearch(params=PARAMS, seed=0, npoints=10)
params = [x for x in rs]
kw = rs.process_params(params[0])
kw['all_inputs'] = True
kw['multiple_outputs'] = True
kw['population_class'] = 'Generational'

evo = Evo(**kw)
evo.X = c.X
evo.nclasses(c.y)
evo.y = c.y

