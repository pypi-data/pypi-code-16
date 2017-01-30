import SpectralToolbox.Spectral1D as S1D
import orthpol

P = S1D.HermiteProbabilistsPolynomial()
(a,b) = P.RecursionCoeffs(10)
m_nnorm = orthpol.monomials(a,b,False)
m_norm = orthpol.monomials(a,b,True)