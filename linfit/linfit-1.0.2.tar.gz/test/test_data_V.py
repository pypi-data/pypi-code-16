import numpy as np
import matplotlib.pyplot as plt
from linfit import MockData_perp as MockData

# Reproducible results!
np.random.seed(123)

# Choose the "true" parameters.
#theta = -0.757
theta = np.arctan(-0.9594)
b = 4.294
V = 0.129

# Generate some synthetic data from the model.
N = 50
retDict = MockData(theta, b, sqrtV=np.sqrt(V), ndata=N, xep=[0.1, 0.6], yep=[0.1, 0.6])
x = retDict["x"]
y = retDict["y"]
xerr = retDict["xerr"]
yerr = retDict["yerr"]
flag = np.zeros(N, dtype=bool)
#lou = [3, 9, 17]
lou = []
for loop in lou:
    flag[loop] = 1
    print y[loop]
    while(3*yerr[loop] < y[loop]):
        yerr[loop] *= 1.5
    y[loop] = yerr[loop] * 3
    print y[loop]

#Save the data
scp = "V" #"upp"
# Plot the dataset and the true model.
xl = np.array([0, 10.8])
uflag = flag == 0
plt.errorbar(x[uflag], y[uflag], xerr=xerr[uflag], yerr=yerr[uflag], fmt=".k")
plt.errorbar(x[flag], y[flag], xerr=xerr[flag], yerr=0.5, uplims=True, fmt=".k")
plt.plot(xl, np.tan(theta)*xl+b, "k", lw=3, alpha=0.6)
plt.xlim(0, 10.8)
plt.ylim(-10, 10)
plt.xlabel("$x$")
plt.ylabel("$y$")
plt.tight_layout()
plt.savefig("examples/line-data_{0}.png".format(scp))
plt.close()

data = np.array([x, y, xerr, yerr, flag])
fname = "examples/data_{0}.txt".format(scp)
np.savetxt(fname, data.T, fmt="%.4f")
