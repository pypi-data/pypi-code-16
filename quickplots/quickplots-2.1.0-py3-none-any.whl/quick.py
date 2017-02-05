from omnicanvas import colors
from .series import LineSeries, ScatterSeries
from .charts import AxisChart

def line(*args, **kwargs):
    """This function creates a line chart. Specifcally it creates an
    :py:class:`.AxisChart` and then adds a :py:class:`.LineSeries` to it.

    :param \*data: The data for the line series as either (x,y) values or two\
    big tuples/lists of x and y values respectively.
    :param str name: The name to be associated with the series.
    :param str color: The hex colour of the line.
    :param str linestyle: The line pattern. See\
    `OmniCanvas docs <https://omnicanvas.readthedocs.io/en/latest/api/graphics.\
    html#omnicanvas.graphics.ShapeGraphic.line_style>`_ for acceptable values.
    :raises ValueError: if the size and length of the data doesn't match either\
    format.
    :param Number linewidth: The width in pixels of the data points' edge.
    :param str title: The chart's title. This will be displayed at the top of\
    the chart.
    :param width: The width in pixels of the chart.
    :param height: The height in pixels of the chart.
    :param str x_label: The label for the x-axis.
    :param str y_label: The label for the y-axis.
    :rtype: :py:class:`.AxisChart`"""

    line_series_kwargs = {}
    for kwarg in ("name", "color", "linestyle", "linewidth"):
        if kwarg in kwargs:
            line_series_kwargs[kwarg] = kwargs[kwarg]
            del kwargs[kwarg]
    if "color" not in line_series_kwargs:
        line_series_kwargs["color"] = colors[0]
    series = LineSeries(*args, **line_series_kwargs)
    chart = AxisChart(series, **kwargs)
    return chart


def scatter(*args, **kwargs):
    """This function creates a scatter chart. Specifcally it creates an
    :py:class:`.AxisChart` and then adds a :py:class:`.ScatterSeries` to it.

    :param \*data: The data for the scatter series as either (x,y) values or two\
    big tuples/lists of x and y values respectively.
    :param str name: The name to be associated with the series.
    :param str color: The hex colour of the data points.
    :param Number size: The size of each data point - generally the diameter.
    :param Number linewidth: The width in pixels of the data points' edge.
    :raises ValueError: if the size and length of the data doesn't match either\
    format.
    :param str title: The chart's title. This will be displayed at the top of\
    the chart.
    :param width: The width in pixels of the chart.
    :param height: The height in pixels of the chart.
    :param str x_label: The label for the x-axis.
    :param str y_label: The label for the y-axis.
    :rtype: :py:class:`.AxisChart`"""

    scatter_series_kwargs = {}
    for kwarg in ("name", "color", "size", "linewidth"):
        if kwarg in kwargs:
            scatter_series_kwargs[kwarg] = kwargs[kwarg]
            del kwargs[kwarg]
    if "color" not in scatter_series_kwargs:
        scatter_series_kwargs["color"] = colors[0]
    series = ScatterSeries(*args, **scatter_series_kwargs)
    chart = AxisChart(series, **kwargs)
    return chart
