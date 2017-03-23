import matplotlib.pyplot as plt

bokeh2matplotlib_colors = {
    'blue': 'b',
    'green': 'g',
    'red': 'r',
    'cyan': 'c',
    'magenta': 'm',
    'yellow': 'y',
    'black': 'k',
    'white': 'w',
}

bokeh2matplotlib_markers = {
    'circle': 'o',
    'square': 's',
    'triangle': 'v',
    'asterisk': '*',
    'inverted_triangle': '^',
    'diamond': 'D',
    'cross': 'x',
}


def plot_one_line(x, y, y_errorbar=None, figsize=(15, 9), x_label='', y_label='', y2_label='',
                  line_color=None, data_label='', line_style='-',
                  line_width=2, xlim=None, ylim=None, y2lim=None, show=False, fig=None, y_secondary=False,
                  ticks_font_size=18, label_font_size=18, legend_font_size=18, pad=10,
                  border_thickness=2.0, ticks_length=5.0, ticks_width=2.0, legend_loc='best', fill_alpha=0.3,
                  legend_ncol=1, ylabelpad=None, y2labelpad=None, xlabelpad=None):

    if line_color is None:
        line_color = 'blue'

    if fig is None:
        fig = {
            'fig': None,
            'ax': None,
            'ax2': None,
            'lns': list(),
            'labs': list(),
        }

    if fig['fig'] is None:
        fig['fig'], fig['ax'] = plt.subplots(1, 1, figsize=figsize)

    current_ax = fig['ax']
    if y_secondary and fig['ax2'] is None:
        fig['ax2'] = plt.twinx(fig['ax'])
        current_ax = fig['ax2']

    ln = current_ax.plot(x, y, color=line_color, linestyle=line_style, linewidth=line_width, label=data_label)
    if y_errorbar is not None:
        current_ax.fill_between(x, y-y_errorbar/2.0, y+y_errorbar/2.0, facecolor=line_color, alpha=fill_alpha)

    lab = ln[0].get_label()
    if data_label not in ['', None]:
        fig['lns'].append(ln[0])
        fig['labs'].append(lab)

    if show:
        if xlim:
            fig['ax'].set_xlim(xlim)
        if ylim:
            fig['ax'].set_ylim(ylim)
        if y2lim:
            fig['ax2'].set_ylim(y2lim)

        fig['ax'].set_xlabel(x_label, fontsize=label_font_size)
        fig['ax'].set_ylabel(y_label, fontsize=label_font_size)

        if fig['lns'] != []:
            current_ax.legend(fig['lns'], fig['labs'], loc=legend_loc, fontsize=legend_font_size,
                              ncol=legend_ncol)

        fig['ax'].tick_params(axis='both', which='major', labelsize=ticks_font_size)
        fig['ax'].tick_params(direction='inout', pad=pad)
        [i.set_linewidth(border_thickness) for i in fig['ax'].spines.values()]
        fig['ax'].tick_params('both', direction="in", length=ticks_length, width=ticks_width, which='major')

        if xlabelpad:
            fig['ax'].xaxis.labelpad = xlabelpad
        if ylabelpad:
            fig['ax'].yaxis.labelpad = ylabelpad

        if fig['ax2'] is not None:
            fig['ax2'].set_ylabel(y2_label, fontsize=label_font_size)
            fig['ax2'].tick_params(axis='both', which='major', labelsize=ticks_font_size)
            fig['ax2'].tick_params(direction='inout', pad=pad)
            [i.set_linewidth(border_thickness) for i in fig['ax2'].spines.itervalues()]
            fig['ax2'].tick_params('both', direction="in", length=ticks_length, width=ticks_width, which='major')
            if y2labelpad:
                fig['ax2'].yaxis.labelpad = y2labelpad

    return fig


def plot_one_scatter(x, y, err_x=None, err_y=None, figsize=(15, 9), x_label='', y_label='', data_label='',
                     size=1, show=False, fig=None, marker='circle', alpha=1.0, fill_color='blue',
                     line_color='blue', legend_fill_alpha=0.5, xlim=None, ylim=None,
                     ticks_font_size=20, label_font_size=40, legend_font_size=20, pad=20,
                     border_thickness=3.0, ticks_length=5.0, ticks_width=2.0, legend_loc='best',
                     err_line_width=2.0, err_every=1, err_capthick=2.0, err_capsize=2.0):

    assert marker in bokeh2matplotlib_markers.keys(), 'only these markers are supported: {}'.format(bokeh2matplotlib_markers.keys())

    if line_color is None:
        line_color = 'blue'

    if fill_color is None:
        fill_color = 'blue'

    assert line_color in bokeh2matplotlib_colors.keys(), 'only these colors are supported: {}'.format(bokeh2matplotlib_colors.keys())

    if fig is None:
        f, a = plt.subplots(1, 1, figsize=figsize)
        fig = {
            'fig': f,
            'ax': a,
        }

    if (err_x is not None) or (err_y is not None):
        fig['ax'].errorbar(x, y, xerr=err_x, yerr=err_y, ecolor=bokeh2matplotlib_colors[line_color],
                           elinewidth=err_line_width, errorevery=err_every,
                           ms=size, alpha=alpha, fmt=bokeh2matplotlib_markers[marker],
                           label=data_label, markerfacecolor=bokeh2matplotlib_colors[fill_color],
                           markeredgecolor=bokeh2matplotlib_colors[line_color], capthick=err_capthick,
                           capsize=err_capsize)
    else:
        fig['ax'].scatter(x, y, s=size, alpha=alpha, marker=bokeh2matplotlib_markers[marker],
                          label=data_label, c=bokeh2matplotlib_colors[fill_color],
                          edgecolors=bokeh2matplotlib_colors[line_color])

    if show:
        if xlim:
            fig['ax'].set_xlim(xlim)
        if ylim:
            fig['ax'].set_ylim(ylim)

        fig['ax'].set_xlabel(x_label, fontsize=label_font_size)
        fig['ax'].set_ylabel(y_label, fontsize=label_font_size)

        fig['ax'].legend(loc=legend_loc, fontsize=legend_font_size)

        fig['ax'].tick_params(axis='both', which='major', labelsize=ticks_font_size)
        fig['ax'].tick_params(direction='inout', pad=pad)

        [i.set_linewidth(border_thickness) for i in fig['ax'].spines.itervalues()]

        fig['ax'].tick_params('both', direction='in', length=ticks_length, width=ticks_width, which='major')

    return fig
