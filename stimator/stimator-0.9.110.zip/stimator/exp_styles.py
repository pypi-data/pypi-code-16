
import matplotlib as mpl
from matplotlib import style as st
import matplotlib.pyplot as plt
print(st.available)

for name in st.available:
    print('----------------------------')
    print(name)
    plt.style.use(name)
    print('----------------------------')
    for (k, v) in mpl.rcParams.items():
        print(k, v)
    