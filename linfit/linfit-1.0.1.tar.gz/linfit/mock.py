import numpy as np
import matplotlib.pyplot as plt

def MockData(m, b, lnf=None, sigy=None, x=None, ndata=None, xep=[0.0, 0.0], yep=[0.0, 0.0]):
    """
    Generate the mock data.

    Parameters
    ----------
    m : float
        The slope.
    b : float
        The intercept.
    lnf : float, optional (not with sigy)
        The intrinsic scatter as a fraction of the model. The default is None.
    sigy : float, optional (not with lnf)
        The intrinsic scatter as the dispersion in Y axis. The default is None.
    x : float array, optional
        The x of the data. The default is None.
    ndata : float, optional
        If x is not provided, ndata should be given to provide the number of the
        data randomly generated. The default is None.
    xep : list
        The lower and upper boundaries of the x error. The uncertainties are assumed
        to be Gaussian. The default is [0.0, 0.0].
    yep : list
        The lower and upper boundaries of the y error. The uncertainties are assumed
        to be Gaussian. The default is [0.0, 0.0].
    """
    if x is None:
        assert not ndata is None
        x = np.sort(10*np.random.rand(ndata))
    else:
        if (not ndata is None) & (ndata != len(x)):
            raise Warning("[linfit]: The input ndata ({0}) is not used.".format(ndata))
        ndata = len(x)
    xerr = xep[0] + (xep[1] - xep[0]) * np.random.rand(ndata)
    yerr = yep[0] + (yep[1] - yep[0]) * np.random.rand(ndata)
    x += xerr * np.random.randn(ndata)
    plt.figure()
    y = m * x + b
    plt.plot(x, y, linestyle="none", marker=".", label="origin")
    if not lnf is None:
        assert sigy is None
        f = np.exp(lnf)
        y += np.abs(f * y) * np.random.randn(ndata)
        plt.plot(x, y, linestyle="none", marker=".", label="intr. scatt.")
    if not sigy is None:
        assert lnf is None
        y += sigy * np.random.randn(ndata)
        plt.plot(x, y, linestyle="none", marker=".", label="intr. scatt.")
    y += yerr * np.random.randn(ndata)
    plt.plot(x, y, linestyle="none", marker=".", label="measure")
    plt.legend(fontsize=18)
    retDict = {
        "x": x,
        "y": y,
        "xerr": xerr,
        "yerr": yerr
    }
    return retDict

def MockData_perp(theta, b, sqrtV=None, x0=None, ndata=None, xep=[0.0, 0.0], yep=[0.0, 0.0]):
    """
    Generate the mock data with intrinsic scatter perpendicular to the line.

    Parameters
    ----------
    theta : float
        The slope.
    b : float
        The intercept.
    sqrtV : float, optional
        The intrinsic scatter perpendicular to the line. The default is None.
    x0 : float array, optional
        The x of the data along the line. The default is None.
    ndata : float, optional
        If x is not provided, ndata should be given to provide the number of the
        data randomly generated. The default is None.
    xep : list
        The lower and upper boundaries of the x error. The uncertainties are assumed
        to be Gaussian. The default is [0.0, 0.0].
    yep : list
        The lower and upper boundaries of the y error. The uncertainties are assumed
        to be Gaussian. The default is [0.0, 0.0].
    """
    if x0 is None:
        assert not ndata is None
        x0 = np.sort(10*np.random.rand(ndata))
    else:
        if (not ndata is None) & (ndata != len(x)):
            raise Warning("[linfit]: The input ndata ({0}) is not used.".format(ndata))
        ndata = len(x0)
    #Make dispersion perpendicular to the line
    y0 = sqrtV * np.random.randn(ndata)
    #Rotate the line
    vecs = np.array([x0, y0])
    rotMatrix = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    vecsR = np.dot(rotMatrix, vecs)
    x = vecsR[0, :]
    y = vecsR[1, :] + b
    #Add measurement uncertainty
    xerr = xep[0] + (xep[1] - xep[0]) * np.random.rand(ndata)
    yerr = yep[0] + (yep[1] - yep[0]) * np.random.rand(ndata)
    x += xerr * np.random.randn(ndata)
    y += yerr * np.random.randn(ndata)
    retDict = {
        "x": x,
        "y": y,
        "xerr": xerr,
        "yerr": yerr
    }
    return retDict
