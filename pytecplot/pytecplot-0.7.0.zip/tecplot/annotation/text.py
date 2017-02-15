from collections import namedtuple

from .annotation import Annotation
from .annotation import annotation_preamble
from ..constant import *
from ..tecutil import _tecutil, lock
from ..exception import *


class TextBox(object):
    """The Box surrounding the `text <Text>` object

    Warning:
        `TextBox` objects cannot be created directly. They are returned by the
        `Text.text_box` read-only property.
    """

    def __init__(self, uid, frame):
        self.uid = uid
        self.frame = frame

    def __str__(self):
        """Brief string representation"""

        _, text_string = _tecutil.TextGetString(self.uid)
        return 'Text Box attached to Text "{}"'.format(text_string)

    @property
    @annotation_preamble
    def line_thickness(self):
        """Get or set the `text box <TextBox>` line thickness of a
        `text object <Text>`.

        The line thickness must be greater than 0.0.
        (default = 0.1)

        :type: `float <float>`

        Example showing how to set the line thickness of the
        `text box <TextBox>` for a `text <Text>` object::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled
            >>> text.text_box.line_thickness = 0.5
            >>> text.text_box.line_thickness
            0.5

        Raises:
            `TecplotLogicError`
        """
        return _tecutil.TextBoxGetLineThickness(self.uid)

    @line_thickness.setter
    @annotation_preamble
    def line_thickness(self, line_thickness):
        with lock():
            if __debug__ and line_thickness <= 0.0:
                raise TecplotLogicError(
                    'TextBox line thickness must be greater than 0.0')

            _tecutil.TextBoxSetLineThickness(self.uid, float(line_thickness))

    @property
    @annotation_preamble
    def margin(self):
        """Get or set the margin between the text and the
           `text box <TextBox>` surrounding the `text <Text>` object.

           Specify the margin as a percentage of the text character height.
           Margin must be greater than or equal to
           0.0, and may be greater than 100. (default = 20.0)

           :type: `float <float>`

           Example showing how to set the margin of the `text box <TextBox>`
           for a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled
            >>> text.text_box.margin = 0.5
            >>> text.text_box.margin
            0.5


        Raises:
            `TecplotLogicError`
        """
        return _tecutil.TextBoxGetMargin(self.uid)

    @margin.setter
    @annotation_preamble
    def margin(self, margin):
        with lock():
            if __debug__ and margin < 0.0:
                raise TecplotLogicError('TextBox margin must be >= 0.0')

            _tecutil.TextBoxSetMargin(self.uid, float(margin))

    @property
    @annotation_preamble
    def fill_color(self):
        """Get or set the fill color of
        the `text box <TextBox>` for a `text object <Text>`.
        (default = `Color.White`)

        :type: `Color`

        Example showing how to set the fill color of the `text box <TextBox>`
           for a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled
            >>> text.text_box.fill_color = Color.Blue
            >>> text.text_box.fill_color
            Color.Blue

        Raises:
            `TecplotLogicError`
        """
        return Color(_tecutil.TextBoxGetFillColor(self.uid))

    @fill_color.setter
    @annotation_preamble
    def fill_color(self, color):
        with lock():
            _tecutil.TextBoxSetFillColor(self.uid, color.value)

    @property
    @annotation_preamble
    def color(self):
        """Get or set the outline color of the `text box <TextBox>` for
        a `text object <Text>`.

        (default = `Color.Black`)

        :type: `Color`

        Example showing how to set the outline color of the `text box <TextBox>`
           for a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled
            >>> text.text_box.color = Color.Blue
            >>> text.text_box.color
            Color.Blue

        Raises:
            `TecplotLogicError`
        """
        return Color(_tecutil.TextBoxGetColor(self.uid))

    @color.setter
    @annotation_preamble
    def color(self, color):
        with lock():
            _tecutil.TextBoxSetColor(self.uid, color.value)

    _Position = namedtuple('Position', 'x1 y1 x2 y2 x3 y3 x4 y4')

    @property
    @annotation_preamble
    def position(self):
        """Get the position of the four corners of the `text box <TextBox>`
            surrounding the `text object <Text>`.

            **Note:** This property is read-only.

            :type: 8-`tuple` of `floats <float>`

            * x1: X-Coordinate for bottom left corner of the `TextBox`.
            * y1: Y-Coordinate for bottom left corner of the `TextBox`.
            * x2: X-Coordinate for bottom right corner of the `TextBox`.
            * y2: Y-Coordinate for bottom right corner of the `TextBox`.
            * x3: X-Coordinate for upper right corner of the `TextBox`.
            * y3: Y-Coordinate for upper right corner of the `TextBox`.
            * x4: X-Coordinate for upper left corner of the `TextBox`.
            * y4: Y-Coordinate for upper left corner of the `TextBox`.

        (no default, position will vary with text box properties)

        Example showing how to query position of the `text box <TextBox>`
           for a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled
            >>> x1,y1,x2,y2,x3,y3,x4,y4 = text.text_box.position
            >>> # x1,...,y4 contain the corners of the text box

        Raises:
            `TecplotLogicError`
        """
        return TextBox._Position(*_tecutil.TextBoxGetPosition(self.uid))

    @property
    @annotation_preamble
    def text_box_type(self):
        """Get or set the type of the box surrounding the `text <Text>` object

        :type: `tecplot.constant.TextBox`

        The text box type can be set to the following:

            * None\_ - Select this option to specify that no box is drawn around
                the text.
            * Filled - Select this option to specify a filled box around the
                text.
                A filled box is opaque; if you place it over another
                |Tecplot 360 EX| object, the underlying object cannot be seen.
            * Hollow - Select this to specify a plain box around the text.

        (default = `TextBox.None\_`

        Example showing how to set the type of the text box for a `text <Text>`
        object::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.text_box_type = TextBox.Filled
            >>> text.text_box.text_box_type
            TextBox.Filled

        Raises:
            `TecplotLogicError`
        """
        return _tecutil.TextBoxGetType(self.uid)

    @text_box_type.setter
    @annotation_preamble
    def text_box_type(self, text_box_type):
        with lock():
            _tecutil.TextBoxSetType(self.uid, text_box_type.value)


class Text(Annotation):
    """Text annotation

    Warning:
        `Text` objects cannot be created directly. They are returned by the
        `Frame.add_text()` method.

    """

    def __init__(self, uid, frame):
        super().__init__(uid, frame, Text)
        self._text_box = TextBox(uid, frame)  # type: TextBox

    def __str__(self):
        """Brief string representation.

        Returns:
            `string <str>`: Brief representation of this `Text`.

        Raises:
            `TecplotLogicError`

        Example::
            >>> import tecplot
            >>> frame = tecplot.active_frame()
            >>> print(frame.add_text('Orange'))
            Text: "Orange"
        """
        return self.text_string

    def __eq__(self, other):
        """Checks for `Text` equality in the |Tecplot Engine|.

        Returns:
            `bool`: `True` if the unique ID numbers are the same for both
            `Text objects <Text>`.

        Example::
            >>> import tecplot
            >>> frame = tecplot.active_frame()
            >>> text_1 = frame.add_text('Orange')
            >>> text_2 = frame.add_text('Orange')
            >>> # The literal strings that the `Text` object holds are equal:
            >>> text_1.text_string == text_2.text_string
            True
            >>> # But the `Text` objects themselves are different:
            >>> text_1 == text_2
            False
        """
        return self.uid == other.uid

    def __ne__(self, other):
        """Checks for `Text` inequality in the |Tecplot Engine|.

        Returns:
            `bool`: `True` if the unique ID numbers are not the same for both
            `Text objects <Text>`

        Example::
            >>> import tecplot
            >>> frame = tecplot.active_frame()
            >>> text_1 = frame.add_text('Orange')
            >>> text_2 = frame.add_text('Orange')
            >>> # The literal strings that the `Text` object holds are equal:
            >>> text_1.text_string == text_2.text_string
            True
            >>> # But the `Text` objects themselves are different:
            >>> text_1 == text_2
            False
        """

        return self.uid != other.uid

    def _delete(self):
        _tecutil.TextDelete(self.uid)
        self.uid = TECUTIL_BAD_ID

    @property
    def text_box(self):
        """Get the `TextBox` object for this `Text` object.

        The text box is a box that is drawn around the text. Note that
        in order to show the text box, you must set TextBox.type to a value
        other than TextBox.None.

       :type: `TextBox`

       **Note:** This property is read-only.

       Example showing how to enable the text box::
           for a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.text_box.type = TextBox.Filled # Show the text box

        Raises:
            `TecplotLogicError`
        """
        return self._text_box

    @property
    @annotation_preamble
    def typeface(self):
        """The font family used by the `Text` object.

        :type: `string <str>`

        For consistency across various platforms, |Tecplot 360 EX| guarantees
        that the following standard typeface names are available:

        * "Helvetica"
        * "Times"
        * "Courier"
        * "Greek"
        * "Math"
        * "User Defined".

        Other typefaces may or may not be available depending on the TrueType
        fonts available. If the typeface or style is not available, a suitable
        replacement will be selected.

        Example showing how to set the typeface of a `text object <Text>` to
        'Times'::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.typeface = 'Times'
            >>> text.typeface
            'Times'

        Raises:
            `TecplotLogicError`
        """
        return _tecutil.TextGetTypefaceFamily(self.uid)

    @typeface.setter
    @annotation_preamble
    def typeface(self, typeface):
        with lock():
            _tecutil.TextSetTypeface(
                self.uid,
                typeface,
                _tecutil.TextGetTypefaceIsBold(self.uid),
                _tecutil.TextGetTypefaceIsItalic(self.uid))

    @property
    @annotation_preamble
    def bold(self):
        """Get or set bold typeface of the `text object <Text>`

        :type: `boolean <bool>`

        Example showing how to set the bold property
        of a `text object <Text>`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.typeface = 'Times'
            >>> text.bold = True
            >>> text.bold
            True

        Raises:
            `TecplotLogicError`
        """
        return _tecutil.TextGetTypefaceIsBold(self.uid)

    @bold.setter
    @annotation_preamble
    def bold(self, is_bold):
        with lock():
            _tecutil.TextSetTypeface(self.uid,
                                     _tecutil.TextGetTypefaceFamily(self.uid),
                                     is_bold,
                                     _tecutil.TextGetTypefaceIsItalic(self.uid))

    @property
    @annotation_preamble
    def italic(self):
        """Get or set italic typeface of the `text object <Text>`

        :type: `boolean <bool>`

        Example showing how to set the italic property
        of a `text object <Text>`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.typeface = 'Times'
            >>> text.italic = True
            >>> text.italic
            False

        Raises:
            `TecplotLogicError`
        """
        return _tecutil.TextGetTypefaceIsItalic(self.uid)

    @italic.setter
    @annotation_preamble
    def italic(self, is_italic):
        with lock():
            _tecutil.TextSetTypeface(self.uid,
                                     _tecutil.TextGetTypefaceFamily(self.uid),
                                     _tecutil.TextGetTypefaceIsBold(self.uid),
                                     is_italic)

    @property
    @annotation_preamble
    def size(self):
        """Get or set the text size in the currently defined text size units.

        :type: `integer <int>`

        Example showing how to set the text size of a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text('abc')
            >>> text.size_units = Units.Point
            >>> text.size = 14
            >>> text.size
            14

        Raises:
            `TecplotLogicError`
        """
        return _tecutil.TextGetHeight(self.uid)

    @size.setter
    @annotation_preamble
    def size(self, value):
        with lock():
            _tecutil.TextSetHeight(self.uid, value)

    @property
    @annotation_preamble
    def anchor(self):
        """Get or set the anchor style for a `text object <Text>`.

        :type: `TextAnchor`

        Specify the anchor point, or fixed point, for the text object.
        As the text object grows or shrinks, the anchor location is fixed,
        while the rest of the box adjusts to accommodate the new size.
        (default = `TextAnchor.Left`)

        There are nine possible anchor position points, corresponding to the
        left, right, and center positions on the headline, midline,
        and baseline of the text box.

        Example showing how to set the anchor of a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text('abc')
            >>> text.anchor = TextAnchor.Center
            >>> text.anchor
            TextAnchor.Center

        Raises:
            `TecplotLogicError`
        """
        return TextAnchor(_tecutil.TextGetAnchor(self.uid))

    @anchor.setter
    @annotation_preamble
    def anchor(self, text_anchor):
        with lock():
            _tecutil.TextSetAnchor(self.uid, text_anchor.value)

    @property
    @annotation_preamble
    def angle(self):
        """Get or set the text angle in degrees for a `text object <Text>`

        :type: `float <float>` in degrees.

        The text angle is the orientation of the text relative to the axis.
        The angle is measured in degrees counter-clockwise from horizontal.
        Horizontal text is at zero degrees; vertical text is at 90 degrees.

        Example showing how to set the angle of a `text object <Text>`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.angle = 45
            >>> text.angle
            45.0

        Raises:
            `TecplotLogicError`
        """
        return _tecutil.TextGetAngle(self.uid)

    @angle.setter
    @annotation_preamble
    def angle(self, angle):
        with lock():
            _tecutil.TextSetAngle(self.uid, float(angle))

    @property
    @annotation_preamble
    def position_coordinate_system(self):
        """Get or Set the position coordinate
        system of the `text object <Text>`.

        The text object may be positioned using either the grid coordinate
        system or the frame coordinate system.

        If the position_coordinate_system is `CoordSys.Frame`, then the
        size_units property must be `Units.Frame` or `Units.Point`.

        The text object's position and text height are adjusted so that it
        remains identical to its visual appearance in the original
        coordinate and unit system.

        :type: `CoordSys`, must be either `CoordSys.Frame` or `CoordSys.Grid`

        If the size units are `Units.Grid` and the position coordinate system
        is changed to `CoordSys.Frame`, then the size units will be changed
        to `Units.Frame`. (default = CoordSys.Frame)

        Example showing how to set the position coordinate system
        for a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.position_coordinate_system = CoordSys.Grid
            >>> text.position_coordinate_system
            CoordSys.Grid


        Example showing side effect if size units are `CoordSys.Grid` and
        the coordinate system is changed to `CoordSys.Frame`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text("abc")
            >>> text.size_units = Units.Grid
            >>> text.size_units
            Units.Grid
            >>> # Setting the coord sys to frame will change the units to frame.
            >>> text.position_coordinate_system = CoordSys.Frame
            >>> text.position_coordinate_system
            CoordSys.Frame
            >>> text.size_units
            Units.Frame

        """
        return CoordSys(_tecutil.TextGetPositionCoordSys(self.uid))

    @position_coordinate_system.setter
    @annotation_preamble
    def position_coordinate_system(self, coord_sys):
        with lock():
            size_units = _tecutil.TextGetSizeUnits(self.uid)
            if size_units == Units.Grid and coord_sys == CoordSys.Frame:
                # Set units to be frame to avoid an illegal combination
                # which would TU_ASSERT
                size_units = Units.Frame

            _tecutil.TextSetCoordSysAndUnits(
                self.uid, coord_sys.value, size_units.value)

    @property
    @annotation_preamble
    def size_units(self):
        """Specify the units of the text character size.

        :type: `Units`

        `Units` may be one of the following:

            * `Units.Point`: Specify character height in points.
            * `Units.Frame`: Specify character height as a percentage of frame height
            * `Units.Grid`: Specify character height in grid units.

        (default = `Units.Point`)

        Notes::
            * One point is 1/72nd of an inch.
            * `Units.Grid` is available only if position_coordinate_system is `CoordSys.Grid`
            * The position coordinate system will be changed to `CoordSys.Grid` if size units is set to `Units.Grid`

        Example showing how to set the units of the character height
        for a `text object <Text>`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.position_coordinate_system = CoordSys.Grid
            >>> text.size_units = Units.Point
            >>> text.size_units
            Units.Point

        Raises:
            `TecplotLogicError`
        """
        return Units(_tecutil.TextGetSizeUnits(self.uid))

    @size_units.setter
    @annotation_preamble
    def size_units(self, size_units):
        with lock():
            coord_sys = _tecutil.TextGetPositionCoordSys(self.uid)
            if size_units == Units.Grid:
                coord_sys = CoordSys.Grid

            _tecutil.TextSetCoordSysAndUnits(
                self.uid, coord_sys.value, size_units.value)

    @property
    @annotation_preamble
    def line_spacing(self):
        """Get or set the line spacing for the `text object <Text>`


        :type: `float <float>`

        Line spacing is dependent on the height of the text and the size unit
        system in which it is drawn. (default = 1.0)

        Example showing how to set the line spacing of a `text object <Text>`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.line_spacing = 4
            >>> text.line_spacing
            4.0

        Raises:
            `TecplotLogicError`
        """
        return _tecutil.TextGetLineSpacing(self.uid)

    @line_spacing.setter
    @annotation_preamble
    def line_spacing(self, line_spacing):
        with lock():
            _tecutil.TextSetLineSpacing(self.uid, float(line_spacing))

    @property
    @annotation_preamble
    def text_string(self):
        """Get or set the text string of the `text object <Text>`

        :type: `string <str>`

        You can embed Greek, Math, and User-defined characters into English-font
        strings by enclosing them with text formatting tags,
        together with the keyboard characters.

        The text formatting tags and their effects are as follows
        (format tags are not case sensitive and may be either
        upper or lower case):

        * <b>...</b> - Boldface
        * <i>...</i> - Italic
        * <verbatim>...</verbatim> - Verbatim
        * <sub>...</sub> - Subscripts
        * <sup>...</sup> - Superscripts
        * <greek>...</greek> - Greek font.
        * <math>...</math> - Math font.
        * <userdef>...</userdef> - User-defined font.
        * <helvetica>...</helvetica> - Helvetica font.
        * <times>...</times> - Times font.
        * <courier>...</courier> - Courier font.

        Not all fonts have Bold and/or Italic variants.
        For fonts that do not have these styles,
        the <b> and/or <i> tags may have no effect.

        Embedding and escaping special characters work only in English-font
        text; they have no effect in text created in Greek, Math,
        or User-defined character sets.

        You can produce subscripts or superscripts by enclosing any characters
        with <sub>...</sub> or <sup>...</sup>, respectively.
        |Tecplot 360 EX| has only one level of superscripts and subscripts.
        Expressions requiring additional levels
        must be created by hand using multiple text objects.
        If you alternate subscripts and superscripts, |Tecplot 360 EX| positions
        the superscript directly above the subscript.
        To produce consecutive superscripts, enclose all superscript
        characters in a single pair of tags.

        To insert a tag into text literally,
        precede the first angle bracket with a backslash ("\").
        To insert a backslash in the text, just type two backslashes ("\\").

        Example showing how to set the text string of a `text object <Text>`::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text('abc')
            >>> text.text_string
            'abc'
            >>> text.text_string ='def'
            >>> text.text_string
            'def'

        Raises:
            `TecplotSystemError`
            if there is insufficient memory to set the text string.
        """
        result, text_string = _tecutil.TextGetString(self.uid)
        if not result:
            raise TecplotSystemError
        return text_string

    @text_string.setter
    @annotation_preamble
    def text_string(self, text_string):
        with lock():
            _tecutil.TextSetString(self.uid, text_string)
