import numpy as np


def bar(title,
        data,
        xlabel,
        xticklabels,
        ylabel,
        file=None,
        figsize=None,
        xlim=None,
        ylim=None,
        colors=['r', 'b', 'g', 'c', 'm', 'y', 'k']):
    if file:
        import matplotlib
        # must be done before importing plt
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    try:
        import seaborn
    except:
        pass

    fig, ax = plt.subplots()
    bar_width = np.maximum(.05,
                           1. / (len(data.keys()) * len(data.values()[0])))

    index = np.arange(len(data.values()[0]))

    i = 0
    for key, value in data.items():
        try:
            color = colors[i]
        except IndexError:
            color = np.random.rand(3)
        ax.bar(
            index + (i * bar_width), value, bar_width, color=color, label=key)
        i += 1

    plt.title(title)
    plt.xlabel(xlabel)
    plt.xticks(index + ((bar_width * len(data.keys())) / 2), xticklabels)
    plt.ylabel(ylabel)
    plt.legend(loc='best')
    plt.tight_layout()
    plt.ylim(ylim)
    plt.xlim(xlim)

    if file:
        plt.savefig(file, bbox_inches='tight', dpi=300)
    else:
        plt.show()


def plot(title,
         xdata,
         ydata,
         file=None,
         figsize=None,
         xlim=None,
         ylim=None,
         colors=['r', 'b', 'g', 'c', 'm', 'y', 'k'],
         font_size=16):
    if file:
        import matplotlib
        # must be done before importing plt
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    try:
        import seaborn
    except:
        pass

    plt.rcParams.update({'font.size': font_size})
    plt.figure(figsize=figsize)
    plt.title(title)

    for i, y in enumerate(ydata):
        try:
            color = colors[i]
        except IndexError:
            color = np.random.rand(3)

        plt.plot(
            xdata[1],
            y[1],
            '-o',
            label=y[0],
            color=color,
            linewidth=1.5,
            markersize=3.0)
    plt.legend(loc='best')
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xlabel(xdata[0])
    plt.ylabel(", ".join([y[0] for y in ydata]))
    plt.tight_layout()

    if file:
        plt.savefig(file, bbox_inches='tight', dpi=300)
    else:
        plt.show()
