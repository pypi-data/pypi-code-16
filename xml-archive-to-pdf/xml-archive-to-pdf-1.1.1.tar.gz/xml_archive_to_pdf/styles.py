from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import TableStyle
from xml_archive_to_pdf.settings import *
from reportlab.lib.enums import TA_CENTER


def get_styles(fontFamily=DEFAULT_FONT):
    """
    get styles for the pdf, default are :
    Title: <ParagraphStyle ‘Title’>
    Heading1: <ParagraphStyle ‘Heading1’>
    Heading2: <ParagraphStyle ‘Heading2’>
    Heading3: <ParagraphStyle ‘Heading3’>
    Heading4: <ParagraphStyle ‘Heading4’>
    Heading5: <ParagraphStyle ‘Heading5’>
    Heading6: <ParagraphStyle ‘Heading6’>
    Normal: <ParagraphStyle ‘Normal’>
    Italic: <ParagraphStyle ‘Italic’>
    BodyText: <ParagraphStyle ‘BodyText’>
    unused:
    Bullet: <ParagraphStyle ‘Bullet’>
    Definition: <ParagraphStyle ‘Definition’>
    Code: <ParagraphStyle ‘Code’>
    """
    styles = getSampleStyleSheet()
    # Titles
    styles.add(ParagraphStyle(name='cTitle', parent=styles['Title'], fontName="{}-Bold".format(fontFamily), spaceAfter=SPACE_UNIT*2))
    styles.add(ParagraphStyle(name='cHeading1', parent=styles['Heading1'], fontName="{}-Bold".format(fontFamily), spaceBefore=SPACE_UNIT,
        borderRadius=5, borderWidth=1, borderPadding=4, borderColor=colors.HexColor("#668cff"), backColor=colors.HexColor("#668cff")))
    styles.add(ParagraphStyle(name='cHeading2', parent=styles['Heading2'], fontName="{}-Bold".format(fontFamily), spaceBefore=SPACE_UNIT, leftIndent=SPACE_UNIT,
        borderRadius=5, borderWidth=1, borderPadding=4, borderColor=colors.HexColor("#809fff"), backColor=colors.HexColor("#809fff")))
    styles.add(ParagraphStyle(name='cHeading3', parent=styles['Heading3'], fontName="{}-BoldOblique".format(fontFamily), spaceBefore=SPACE_UNIT, leftIndent=SPACE_UNIT*2,
        borderRadius=5, borderWidth=1, borderPadding=4, borderColor=colors.HexColor("#99b3ff"), backColor=colors.HexColor("#99b3ff")))
    styles.add(ParagraphStyle(name='cHeading4', parent=styles['Heading4'], fontName="{}-BoldOblique".format(fontFamily), spaceBefore=SPACE_UNIT, leftIndent=SPACE_UNIT*3,
        borderRadius=5, borderWidth=1, borderPadding=4, borderColor=colors.HexColor("#b3c6ff"), backColor=colors.HexColor("#b3c6ff")))
    styles.add(ParagraphStyle(name='cHeading5', parent=styles['Heading5'], fontName="{}-Bold".format(fontFamily), spaceBefore=SPACE_UNIT, leftIndent=SPACE_UNIT*4,
        borderRadius=5, borderWidth=1, borderPadding=4, borderColor=colors.HexColor("#ccd9ff"), backColor=colors.HexColor("#ccd9ff")))
    styles.add(ParagraphStyle(name='cHeading6', parent=styles['Heading6'], fontName="{}-Bold".format(fontFamily), spaceBefore=SPACE_UNIT, leftIndent=SPACE_UNIT*5,
        borderRadius=5, borderWidth=1, borderPadding=4, borderColor=colors.HexColor("#e6ecff"), backColor=colors.HexColor("#e6ecff")))
    # Normals
    styles.add(ParagraphStyle(name='cNormal', fontName=fontFamily, parent=styles['Normal']))
    styles.add(ParagraphStyle(name='cNormal1', fontName=fontFamily, leftIndent=SPACE_UNIT, parent=styles['Normal']))
    styles.add(ParagraphStyle(name='cNormal2', fontName=fontFamily, leftIndent=SPACE_UNIT*2, parent=styles['Normal'])),
    styles.add(ParagraphStyle(name='cNormal3', fontName=fontFamily, leftIndent=SPACE_UNIT*3, parent=styles['Normal'])),
    styles.add(ParagraphStyle(name='cNormal4', fontName=fontFamily, leftIndent=SPACE_UNIT*4, parent=styles['Normal'])),
    styles.add(ParagraphStyle(name='cNormal5', fontName=fontFamily, leftIndent=SPACE_UNIT*5, parent=styles['Normal'])),
    styles.add(ParagraphStyle(name='cNormal6', fontName=fontFamily, leftIndent=SPACE_UNIT*6, parent=styles['Normal'])),
    # BodyText
    styles.add(ParagraphStyle(name='cBodyText', fontName=fontFamily, alignment=TA_CENTER, parent=styles['BodyText']))
    # Italic
    styles.add(ParagraphStyle(name='cItalic', fontName="{}-Oblique".format(fontFamily), parent=styles['Italic']))

    return styles


def get_title_style(styles, level):
    """ get title style by level """
    if level == 0:
        return styles["cTitle"]
    elif level in [1, 2, 3, 4, 5, 6]:
        return styles["{}{}".format("cHeading", str(level))]
    else:
        return styles["cItalic"]


def get_normal_style(styles, level, odd_even_back=0):
    """ get title style by level """
    if level == 0:
        style = styles["cNormal"]
    elif level in [1, 2, 3, 4, 5, 6]:
        style = styles["{}{}".format("cNormal", str(level))]
    else:
        style = styles["cNormal6"]
    if odd_even_back:
        style.backColor = colors.HexColor("#e6ecff") if odd_even_back % 2 == 0 else colors.HexColor("#ffffff")
    return style


def get_table_style():
    """ get table style """
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ccd9ff")),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#ccd9ff")),
        ('BOX', (0, 0), (-1, -1), 2, "#99b3ff")
    ], hAlign='CENTER', wordWrap='LTR')
