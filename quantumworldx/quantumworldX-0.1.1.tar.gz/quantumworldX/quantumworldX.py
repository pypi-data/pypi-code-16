import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
import matplotlib.animation as manimation
import io
import base64
from IPython.display import HTML

# global variables
COLOR_MAP = 'viridis'

# math utilities


def extend_range(v, percent=0.05):
    vmin, vmax = np.min(v), np.max(v)
    vdiff = (vmax - vmin)
    vmin -= vdiff * percent
    vmax += vdiff * percent
    return vmin, vmax

# time based plotting utilities


def time_colormap(t):
    cmap = mpl.cm.get_cmap(COLOR_MAP)
    norm = mpl.colors.Normalize(vmin=np.min(t), vmax=np.max(t))

    def color_map(v):
        return cmap(norm(v))

    return color_map


def time_colorbar(t):
    cmap = mpl.cm.get_cmap(COLOR_MAP)
    norm = mpl.colors.Normalize(vmin=np.min(t), vmax=np.max(t))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    # fake up the array of the scalar mappable
    sm._A = []
    return sm


def time_plot(x, y, t, t_step=1):

    cmap = time_colormap(t)

    for indt in range(0, len(t), t_step):
        ti = t[indt]
        plt.plot(x, y[:, indt], c=cmap(ti))

    plt.xlim(extend_range(x))
    plt.ylim(extend_range(y))
    plt.xlabel('$x$')
    plt.ylabel('$y$')

    plt.colorbar(time_colorbar(t), label='time ($t$)',
                 orientation='horizontal')
    return
# HTML embbeding codes


def embed_video(afile):
    video = io.open(afile, 'r+b').read()
    encoded = base64.b64encode(video)
    html_code = '''<video alt="test" controls>
                    <source src="data:video/mp4;base64,{0}" type="video/mp4" />
                 </video>'''
    html_view = HTML(data=html_code.format(encoded.decode('ascii')))
    return html_view


def embed_gif(afile):
    gif = io.open(afile, 'r+b').read()
    encoded = base64.b64encode(gif)
    html_code = '''<img src="data:image/gif;base64,{0}">'''
    html_view = HTML(data=html_code.format(encoded.decode('ascii')))
    return html_view

# make videos and gif


def make_movie(x, y, t, t_step=10, title='test'):
    # save backend and switch
    original_backend = plt.get_backend()
    plt.switch_backend('Agg')

    cmap = time_colormap(t)

    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title=title, artist='Matplotlib',
                    comment='QuantumWorldX movie')
    writer = FFMpegWriter(fps=30, metadata=metadata)
    t_step = 10
    plt.clf()
    fig = plt.figure()
    l, = plt.plot([], [], '-', lw=3, label='$t=0.0$')

    plt.xlim(extend_range(x))
    plt.ylim(extend_range(y))
    plt.xlabel('$x$')
    plt.ylabel('$y$')
    plt.legend(loc='lower left')
    plt.colorbar(time_colorbar(t), label='time ($t$)',
                 orientation='horizontal')

    with writer.saving(fig, "{}.mp4".format(title), dpi=100):
        for t_indx in range(0, y.shape[1], t_step):
            ti = t[t_indx]
            l.set_data(x, y[:, t_indx])
            l.set_color(cmap(ti))
            l.set_label('$t={:2.2f}$'.format(ti))
            plt.legend(loc='upper left')
            writer.grab_frame()
    # swtich backend
    plt.switch_backend(original_backend)
    return


def make_gif(x, y, t, t_step=10, title='test'):
    plt.clf()
    cmap = time_colormap(t)

    def init():
        global line
        line, = ax.plot(x, np.zeros_like(x), '-', lw=3, label='$t=0.0$')
        ax.set_xlim(extend_range(x))
        ax.set_ylim(extend_range(y))
        ax.set_xlabel('$x$')
        ax.set_ylabel('$y$')
        ax.legend(loc='lower left')
        fig.colorbar(time_colorbar(t), label='time ($t$)',
                     orientation='horizontal')
        return line,

    def anim(i):
        t_indx = i * t_step
        ti = t[t_indx]
        line.set_data(x, y[:, t_indx])
        line.set_color(cmap(ti))
        line.set_label('$t={:2.2f}$'.format(ti))
        ax.legend(loc='upper left')
        return line,
    fig = plt.figure()
    ax = fig.add_subplot(111)
    n_frames = len(range(0, y.shape[1], t_step))
    ani = manimation.FuncAnimation(
        fig, anim, init_func=init, frames=n_frames, blit=True)
    ani.save('{}.gif'.format(title), writer='imagemagick', fps=30)
    return


if __name__ == "__main__":
    print("Load me as a module please")
