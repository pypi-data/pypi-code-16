class NNModel:
    """Defines common interface and shared code for all variants of the
    nearest-neighbor model (DNA-DNA, RNA-RNA, and DNA-RNA)
    Parameters:
    -----------
    Tref: Float
          reference temperature for thermo data
    R: Float
       gas constant in kcal/mol/K
    pairs: Python dict()
           posible pairs for DNA
    rpairs: Python dict()
            posible pairs for RNA

    Notes:
    ------
    Pairs are written in 5' -> 3' direction
    """
    def __init__(self):
        self.Tref = 37+273.15   # reference temperature for thermo data
        self.R = 1.987e-3       # gas constant in kcal/mol/K

        self.pairs = ['AA', 'AT', 'AC', 'AG', 'TA', 'TT', 'TC', 'TG',
                      'CA', 'CT', 'CC', 'CG', 'GA', 'GT', 'GC', 'GG']
        self.rpairs = ['AA', 'AU', 'AC', 'AG', 'UA', 'UU', 'UC', 'UG',
                       'CA', 'CU', 'CC', 'CG', 'GA', 'GU', 'GC', 'GG']
