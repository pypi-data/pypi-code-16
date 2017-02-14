from bokeh.palettes import brewer

def get_colors(colors, labels):
    if colors is None:
        colors = dict()

        colors_iter = iter(brewer['Spectral'][11])
        for label in labels:
            colors[label] = next(colors_iter)
    return colors
