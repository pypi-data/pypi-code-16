import numpy
import scipy.fftpack

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
import mpld3
from mpld3 import plugins

class Spectrum:

    def __init__(self, properties):
        self.properties = properties

    def show(self, data):
        # fig, ax = plt.subplots()

        y = numpy.fromstring(data['result'], dtype=float, sep=",")
        x = numpy.linspace(
            start=self.properties['frequency_center'] - self.properties['frequency_span'],
            stop=self.properties['frequency_center'] + self.properties['frequency_span'],
            num=y.size)
        #y = np.sin(50.0 * 2.0 * np.pi * x) + 0.5 * np.sin(80.0 * 2.0 * np.pi * x)
        # yf = scipy.fftpack.fft(y)
        # xf = numpy.linspace(0.0, 1.0 / (2.0 * T), N / 2)

        fig, ax = pyplot.subplots()
        # ax.plot(x, 2.0 / N * numpy.abs(y[:N // 2]))
        ax.plot(x, y)

        # plt.show()


        # x = np.linspace(-2, 2, 20)
        # y = x[:, None]
        #
        # X = np.zeros((20, 20, 4))
        # X[:, :, 0] = np.exp(- (x - 1) ** 2 - (y) ** 2)
        # X[:, :, 1] = np.exp(- (x + 0.71) ** 2 - (y - 0.71) ** 2)
        # X[:, :, 2] = np.exp(- (x + 0.71) ** 2 - (y + 0.71) ** 2)
        # X[:, :, 3] = np.exp(-0.25 * (x ** 2 + y ** 2))
        #
        # im = ax.imshow(X, extent=(10, 20, 10, 20), origin='lower', zorder=1, interpolation='nearest')
        # fig.colorbar(im, ax=ax)
        #
        ax.set_title(self.properties['title'], size=20)

        #
        # # plugins.MousePosition(fontsize=14)
        # plugins.connect(fig=fig)

        return  mpld3.fig_to_html(fig=fig)

class Heatmap:

    def __init__(self, properties):
        self.properties = properties

    def show(self, data):
        fig, ax = pyplot.subplots()
        #
        # y = numpy.fromstring(data['result'], dtype=float, sep=",")
        # x = numpy.linspace(
        #     start=self.properties['frequency_center'] - self.properties['frequency_span'],
        #     stop=self.properties['frequency_center'] + self.properties['frequency_span'],
        #     num=y.size)
        # # y = np.sin(50.0 * 2.0 * np.pi * x) + 0.5 * np.sin(80.0 * 2.0 * np.pi * x)
        # yf = scipy.fftpack.fft(y)
        # xf = numpy.linspace(0.0, 1.0 / (2.0 * 10), 401 / 2)
        #
        # fig, ax = pyplot.subplots()
        # ax.plot(x, 2.0 / 401 * numpy.abs(y[:401 // 2]))
        # # ax.plot(x, y)
        #
        # # plt.show()


        x = numpy.linspace(-2, 2, 20)
        y = x[:, None]

        # X = numpy.zeros((20, 20, 4))
        y = numpy.fromstring(data['result'], dtype=float, sep=",")
        X = numpy.asmatrix(y)

        im = ax.imshow(X, extent=(10, 20, 10, 20), origin='lower', zorder=1, interpolation='nearest')
        fig.colorbar(im, ax=ax)

        ax.set_title(self.properties['title'], size=20)

        #
        plugins.MousePosition(fontsize=14)
        plugins.connect(fig=fig)

        return  mpld3.fig_to_html(fig=fig)