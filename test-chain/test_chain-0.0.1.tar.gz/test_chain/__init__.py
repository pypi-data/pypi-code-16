from .test_chain_meta import *

if sys.version_info[0] == 2:
    from .test_chain2 import TestChain
elif sys.version_info[0] == 3:
    from .test_chain3 import TestChain