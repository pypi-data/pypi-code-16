"""
All utils
"""
import xml.etree.cElementTree as ET
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, Indenter
from xml_archive_to_pdf.styles import get_styles, get_title_style, get_normal_style, get_table_style
from xml_archive_to_pdf.settings import *
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from os.path import join
from copy import copy
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont(DEFAULT_FONT, 10)
        self.drawRightString(letter[0]-SPACE_UNIT*2, SPACE_UNIT,
                             "%d/%d" % (self._pageNumber, page_count))


def get_bare_tag(elem):
    """ Get the tag name without namespace """
    return elem.tag.rsplit('}', 1)[-1]


def get_clean_text(elem):
    """ return value without line breaker chars """
    return re.sub(r"[\f\n\r\t\v]", "", elem.text).strip() if elem.text else ""


def get_doc(pdf_file):
    """ get the pdf doc """
    return SimpleDocTemplate(pdf_file, pagesize=letter, rightMargin=SPACE_UNIT*2,
                             leftMargin=SPACE_UNIT*2, topMargin=SPACE_UNIT*2, bottomMargin=SPACE_UNIT*2)


def registerFont(fontFamilyName, folder_path):
    """ register a font """
    # Register a custom font
    pdfmetrics.registerFont(TTFont('{}-Bold'.format(fontFamilyName), join(folder_path, "{}-Bold.ttf".format(fontFamilyName))))
    pdfmetrics.registerFont(TTFont(fontFamilyName, join(folder_path, "{}.ttf".format(fontFamilyName))))
    pdfmetrics.registerFont(TTFont('{}-Oblique'.format(fontFamilyName), join(folder_path, "{}-Oblique.ttf".format(fontFamilyName))))
    pdfmetrics.registerFont(TTFont('{}-BoldOblique'.format(fontFamilyName), join(folder_path, "{}-BoldOblique.ttf".format(fontFamilyName))))
    pdfmetrics.registerFontFamily(
        fontFamilyName,
        normal=fontFamilyName,
        bold='{}-Bold'.format(fontFamilyName),
        italic='{}-Italic'.format(fontFamilyName),
        boldItalic='{}-BoldItalic'.format(fontFamilyName)
    )


def get_label(e):
    """ get a label or a title from element """
    return e.attrib.get(ATTR_NAME) if e.attrib.get(ATTR_NAME) is not None else get_bare_tag(e)


def has_children(e):
    """ true if element has children """
    return True if e.getchildren() else False


def add_logo(Story, logo_file):
    """ add a logo """
    im = Image(logo_file)
    im.hAlign = 'RIGHT'
    Story.append(im)
    Story.append(Spacer(1, SPACE_UNIT))


def ptTomm(pt):
    """ convert pt to mm """
    return pt * 0.352778


def write_table(Story, e, level, styles):
    """ write a full table """
    data = []
    colWidths = []
    # On récupère les lignes
    rows = e.getchildren()
    label = get_label(e)
    # Si on a un label non vide, on l'affiche comme titre
    if label:
        Story.append(Paragraph(label, get_title_style(styles, level)))
    Story.append(Spacer(1, SPACE_UNIT))
    # On affiche le table
    if rows:
        # On récupère les titres du tableau à partir du 1er element
        columns_names = list(map(lambda x: Paragraph("{}{}{}".format("<b>", get_label(x), "</b>"), styles['cBodyText']), rows[0].getchildren()))
        data.append(columns_names)
        colWidths = [((ptTomm(letter[0])-(SPACE_UNIT*2))/len(columns_names))*mm for i in range(0, len(columns_names))]
        # On parcourt les éléments pour les insérer dans le tableau
        for row in rows:
            values = row.getchildren()
            if not values or has_children(values[0]):
                raise Exception("Table {} has malformed elements".format(label))
            if len(columns_names) != len(values):
                raise Exception("Table {} has wrong elements".format(label))
            line_values = list(map(lambda x: Paragraph(get_clean_text(x), styles['cBodyText']), values))
            data.append(line_values)
        # Build the table
        t = Table(data, colWidths=colWidths)
        t.setStyle(get_table_style())
        Story.append(t)
    return Story


def write_elem(Story, e, level, styles, odd_even_back=0):
    """ write element in the pdf """
    # get label and value
    label = get_label(e)
    value = get_clean_text(e)
    # Gestion des titres: un titre est un élément avec des enfants ou avec un style title
    attr_style = e.attrib.get(ATTR_STYLE)
    if has_children(e) or (attr_style and attr_style == ATTR_STYLE_TITLE):
        # Si on a un label non vide, on l'affiche
        if label:
            Story.append(Paragraph(label, get_title_style(styles, level)))
        # Si on a forcé le nom du label à vide, on met juste un petit espace
        else:
            Story.append(Spacer(1, SPACE_UNIT))
    # C'est un element de type clé-valeur, on l'affiche normalement
    else:
        if label or value:
            # copy style for odd/even background
            style = copy(get_normal_style(styles, level, odd_even_back))
            Story.append(Paragraph("<b>{} :</b> {}".format(label, value), style))
    return Story


def is_writable_element(e, action, table_level):
    """ return true if the element is writable """
    return ET.iselement(e) and action == EVENT_START and not table_level[0]


def is_started_table(e, action, table_level):
    """ return true if the element is writable """
    check = ET.iselement(e) and action == EVENT_START and not table_level[0] and \
        e.attrib.get(ATTR_STYLE) and e.attrib.get(ATTR_STYLE) == ATTR_STYLE_TABLE
    return True if check else False


def calcul_level(action, level):
    """ calcul the level """
    if (action == EVENT_START):
        level += 1
    elif (action == EVENT_END):
        level -= 1
    return level


def is_leaving_table(action, level, table_level):
    """ check if the element/action is leaving a table """
    return action == EVENT_END and table_level[0] and table_level[1] == level


def build_pdf(xml_file, pdf_file, logo_file=None, font_folder=None):
    """ build the pdf file """
    # Build the doc and the story
    doc = get_doc(pdf_file)
    # register a font and get styles
    if font_folder:
        registerFont("CustomFont", font_folder)
        styles = get_styles("CustomFont")
    else:
        styles = get_styles()
    Story = []
    # events and level for lxml
    level = 0
    # Add logo
    if logo_file:
        add_logo(Story, logo_file)
    # Variable to know if the element is a table
    table_level = (False, 0)
    count = 0
    # Parse the full xml
    for action, e in ET.iterparse(xml_file, events=(EVENT_START, EVENT_END)):
        # Check if a table start here
        if is_started_table(e, action, table_level):
            table_level = (True, level)
        # Write title and simple key value
        elif is_writable_element(e, action, table_level):
            count += 1 # for odd/even
            Story = write_elem(Story, e, level, styles, count)
            e.clear()
        # Calcul the level
        level = calcul_level(action, level)
        # WARNING : Write the table when living it because of C, MALLOC AND MEMORY
        if is_leaving_table(action, level, table_level):
            table_level = (False, 0)
            Story = write_table(Story, e, level, styles)
            e.clear()

    # build
    doc.build(Story, canvasmaker=NumberedCanvas)
