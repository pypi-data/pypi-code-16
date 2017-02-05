from numerus import is_numeric

class Series:
    """A data series. Series objects represent the data to be plotted onto a
    chart, and are essentially a sequence of x,y numerical values.

    The charts themselves will have subclasses of this class, with specific
    painting methods, but this class defines all the core properties of series.

    They are instantiated by passing in positional arguments for the data. You
    should provide one or more (x,y) data points as either two-tuples or
    two-lists. Alternatively, you can provide a list/tuple of all the x values
    and a seperate list/tuple of all the y-values - the class will know what you
    mean by the size and number of positional arguments it recieves.

    The data given will automatically be ordered by x-value.

    You can also pass the series a name as a keyword argument.

    :param \*data: The data for the series as either (x,y) values or two big \
    tuples/lists of x and y values respectively.
    :param str name: The name to be associated with the series.
    :param str color: The hex colour of the line.
    :raises ValueError: if the size and length of the data doesn't match either\
    format."""

    def __init__(self, *data, color="#000000", name=None):
        self._data = []
        if len(data) == 0:
            raise ValueError("Cannot create Series with no data")

        if len(data) == 2:
            if len(data[0]) != len(data[1]):
                raise ValueError(
                 "x and y data sequences are of unequal length (%i and %i)" % (
                  len(data[0]), len(data[1])
                 )
                )
            for series in data:
                if not isinstance(series, list) and not isinstance(series, tuple):
                    raise TypeError(
                     "Data must be give as lists or tuples, not '%s'" % str(series)
                    )
            if len(data[0]) != 2:
                data = list(zip(data[0], data[1]))

        for point in data:
            if not isinstance(point, list) and not isinstance(point, tuple):
                raise TypeError(
                 "Data must be give as lists or tuples, not '%s'" % str(point)
                )
            for value in point:
                if not isinstance(value, int) and not isinstance(value, float):
                    raise TypeError(
                     "Data point %s contains non-numeric data" % str(point)
                    )
            if len(point) != 2:
                raise ValueError(
                 "Data points must be of length 2, which %s is not" % str(point)
                )
            self._data.append(tuple(point))
        self._data = sorted(self._data, key=lambda k: k[0])

        if not isinstance(color, str):
            raise TypeError("color must be str, not '%s'" % str(color))
        self._color = color
        if not isinstance(name, str) and name is not None:
            raise TypeError("name must be str, not '%s'" % str(name))
        self._name = name
        self._chart = None


    def __repr__(self):
        return "<%s %s(%i data points)>" % (
         self.__class__.__name__,
         "'%s' " % self._name if self._name is not None else "",
         len(self._data)
        )


    def data(self):
        """Returns the series' data as a list of (x,y) values.

        :rtype: ``list``"""

        return list(self._data)


    def color(self, color=None):
        """Returns or sets (if a value is provided) the series' colour.

        :param str color: If given, the series' colour will be set to this.
        :rtype: ``str``"""

        if color is None:
            return self._color
        else:
            if not isinstance(color, str):
                raise TypeError("color must be str, not '%s'" % str(color))
            self._color = color


    def name(self, name=None):
        """Returns or sets (if a value is provided) the series' name.

        :param str name: If given, the series' name will be set to this.
        :rtype: str"""

        if name is None:
            return self._name
        else:
            if not isinstance(name, str) and name is not None:
                raise TypeError("name must be str, not '%s'" % str(name))
            self._name = name


    def chart(self):
        """If this series is associated with a :py:class:`.Chart`, this method
        will return it. Otherwise it will return ``None``."""

        return self._chart


    def smallest_x(self):
        """Returns the smallest x-value in the series."""

        return self.data()[0][0]


    def largest_x(self):
        """Returns the largest x-value in the series."""

        return self.data()[-1][0]


    def smallest_y(self):
        """Returns the smallest y-value in the series."""

        return min([datum[-1] for datum in self.data()])


    def largest_y(self):
        """Returns the largest y-value in the series."""

        return max([datum[-1] for datum in self.data()])


    def add_data_point(self, x, y):
        """Adds a data point to the series.

        :param x: The numerical x value to be added.
        :param y: The numerical y value to be added."""

        if not is_numeric(x):
            raise TypeError("x value must be numeric, not '%s'" % str(x))
        if not is_numeric(y):
            raise TypeError("y value must be numeric, not '%s'" % str(y))
        current_last_x = self._data[-1][0]
        self._data.append((x, y))
        if x < current_last_x:
            self._data = sorted(self._data, key=lambda k: k[0])


    def remove_data_point(self, x, y):
        """Removes the given data point from the series.

        :param x: The numerical x value of the data point to be removed.
        :param y: The numerical y value of the data point to be removed.
        :raises ValueError: if you try to remove the last data point from\
        a series."""

        if len(self._data) == 1:
            raise ValueError("You cannot remove a Series' last data point")
        self._data.remove((x, y))


    def canvas_points(self):
        """Calculates the coordinates that the data should use to paint itself
        to its associated :py:class:`.AxisChart`. This is used internally to
        create the chart.

        :rtype: ``tuple``"""

        if self.chart():
            x_axis_min = self.chart().x_lower_limit()
            y_axis_min = self.chart().y_lower_limit()
            x_axis_max = self.chart().x_upper_limit()
            y_axis_max = self.chart().y_upper_limit()
            chart_width = self.chart().width()
            chart_height = self.chart().height()
            horizontal_padding = self.chart().horizontal_padding()
            vertical_padding = self.chart().vertical_padding()
            horizontal_margin_pixels = horizontal_padding * chart_width
            vertical_margin_pixels = vertical_padding * chart_height
            x_axis_pixels = chart_width - (2 * horizontal_margin_pixels)
            y_axis_pixels = chart_height - (2 * vertical_margin_pixels)
            x_axis_span = x_axis_max - x_axis_min
            y_axis_span = y_axis_max - y_axis_min
            x_pixels_per_point = x_axis_pixels / x_axis_span
            y_pixels_per_point = y_axis_pixels / y_axis_span
            data = []
            for x, y in self.data():
                relative_x, relative_y = x - x_axis_min, y - y_axis_min
                data.append((
                 (relative_x * x_pixels_per_point) + horizontal_margin_pixels,
                 chart_height - ((relative_y * y_pixels_per_point) + vertical_margin_pixels)
                ))
            return tuple(data)



class LineSeries(Series):
    """Base class: :py:class:`Series`

    A :py:class:`Series` which can paint itself in a line-chart style.

    :param \*data: The data for the series as either (x,y) values or two big \
    tuples/lists of x and y values respectively.
    :param str name: The name to be associated with the series.
    :param str color: The hex colour of the line.
    :param str linestyle: The line pattern. See\
    `OmniCanvas docs <https://omnicanvas.readthedocs.io/en/latest/api/graphics.\
    html#omnicanvas.graphics.ShapeGraphic.line_style>`_ for acceptable values.
    :raises ValueError: if the size and length of the data doesn't match either\
    format.
    :param Number linewidth: The width in pixels of the data points' edge."""

    def __init__(self, *args, linestyle="-", linewidth=2, **kwargs):
        Series.__init__(self, *args, **kwargs)

        if not isinstance(linestyle, str):
            raise TypeError("linestyle must be str, not '%s'" % str(linestyle))
        self._linestyle = linestyle
        if not is_numeric(linewidth):
            raise TypeError("linewidth must be number, not '%s'" % str(linewidth))
        self._linewidth = linewidth


    def linestyle(self, linestyle=None):
        """Returns or sets (if a value is provided) the series' linestyle. See\
        `OmniCanvas docs <https://omnicanvas.readthedocs.io/en/latest/api/graph\
        ics.html#omnicanvas.graphics.ShapeGraphic.line_style>`_ for acceptable
        values.

        :param str linestyle: If given, the series' linestyle will be set to\
        this.
        :rtype: ``str``"""

        if linestyle is None:
            return self._linestyle
        else:
            if not isinstance(linestyle, str):
                raise TypeError(
                 "linestyle must be str, not '%s'" % str(linestyle)
                )
            self._linestyle = linestyle


    def linewidth(self, linewidth=None):
        """Returns or sets (if a value is provided) the width of the series'
        line.

        :param Number linewidth: If given, the series' linewidth will be set to\
        this.
        :rtype: ``Number``"""

        if linewidth is None:
            return self._linewidth
        else:
            if not is_numeric(linewidth):
                raise TypeError(
                 "linewidth must be number, not '%s'" % str(linewidth)
                )
            self._linewidth = linewidth


    def write_to_canvas(self, canvas, name):
        """Writes the series to an OmniCanvas canvas.

        :param Canvas canvas: The canvas to write to.
        :param str name: The name to give the line graphic on the canvas."""

        points = self.canvas_points()
        args = []
        for point in points:
            args += list(point)
        canvas.add_polyline(
         *args, line_color=self.color(), line_style=self.linestyle(),
         line_width=self.linewidth(), name=name
        )



class ScatterSeries(Series):
    """Base class: :py:class:`Series`

    A :py:class:`Series` which can paint itself in a scatter-chart style.

    :param \*data: The data for the series as either (x,y) values or two big \
    tuples/lists of x and y values respectively.
    :param str name: The name to be associated with the series.
    :param str color: The hex colour of the line.
    :param Number size: The size of each data point - generally the diameter.
    :param Number linewidth: The width in pixels of the data points' edge."""

    def __init__(self, *args, size=5, linewidth=1, **kwargs):
        Series.__init__(self, *args, **kwargs)

        if not is_numeric(size):
            raise TypeError("size must be number, not '%s'" % str(size))
        self._size = size
        if not is_numeric(linewidth):
            raise TypeError("linewidth must be number, not '%s'" % str(linewidth))
        self._linewidth = linewidth


    def size(self, size=None):
        """Returns or sets (if a value is provided) the diameter of the series'
        data points.

        :param Number size: If given, the series' size will be set to\
        this.
        :rtype: ``Number``"""

        if size is None:
            return self._size
        else:
            if not is_numeric(size):
                raise TypeError(
                 "size must be number, not '%s'" % str(size)
                )
            self._size = size


    def linewidth(self, linewidth=None):
        """Returns or sets (if a value is provided) the width of the series'
        data points' edge.

        :param Number linewidth: If given, the series' linewidth will be set to\
        this.
        :rtype: ``Number``"""

        if linewidth is None:
            return self._linewidth
        else:
            if not is_numeric(linewidth):
                raise TypeError(
                 "linewidth must be number, not '%s'" % str(linewidth)
                )
            self._linewidth = linewidth


    def write_to_canvas(self, canvas, name):
        """Writes the series to an OmniCanvas canvas.

        :param Canvas canvas: The canvas to write to.
        :param str name: The name to give the line graphic on the canvas."""

        points = self.canvas_points()
        for point in points:
            canvas.add_oval(
             point[0] - (self.size() / 2), point[1] - (self.size() / 2),
             self.size(), self.size(),
             fill_color=self.color(), line_width=self.linewidth(), name=name
            )
