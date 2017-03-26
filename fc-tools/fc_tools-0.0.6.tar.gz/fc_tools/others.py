def LabelBaseName(dim,d):
  if (d==dim):
    return r"\Omega"
  if (d+1==dim):
    return r"\Gamma"
  if (d+2==dim):
    return r"\partial\Gamma"
  if (d+3==dim):
    return r"\partial^2\Gamma"
    
    
def LabelBaseNameSimp(dim,d,ds):
  if (d==dim):
    return LabelBaseName(dim,ds)
  if (d+1==dim):
    return LabelBaseName(dim,ds+1)
  if (d+2==dim):
    return LabelBaseName(dim,ds+2)
  if (d+3==dim):
    return LabelBaseName(dim,ds+3)
