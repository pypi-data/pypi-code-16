import os
import urllib

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import landscape as set_landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image
from reportlab.platypus import ImageAndFlowables
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.rl_config import canvas_basefontname as _baseFontName, baseUnderlineProportion as _baseUnderlineProportion
from .utils import types


class Builder(object):
    """
    Gerador de relatorios em pdf
    """
    def __init__(self, empresa, title, columns_width, table_header, table_data, buffer, report_type=types.TABLE, table_footer=None, header=None, filename_logo=None, show_pages=True, landscape=False, extra_tables=[]):
        """
        Contrutor do relatorio
        :param title: Titulo
        :param header: Dicionario com outros valores filtros no relatório
        :param columns_width: Lista com as larguras das colunas em porcentagem
        :param table_header: lista com titulos de cada coluns da tabela
        :param table_data: lista com o valores a serem inseridos na tabela
        :param table_footer: lista com o footer do relatorio
        :param buffer: Buffer de geração
        :param report_type: Tipo do relatório, TABLE, GRAPH, NORMAL, CUSTOM
        :param filename_logo: caminho do arquivo da imagem do relatório, caso não passe sea usado um padrão
        :param show_pages: Se quizer que apareça as paginas, caso contrario coloque False
        :param landscape: True para relatorio em paisagem, por default é False
        :param extra_tables: lista de tabelas extras
        """
        self.empresa = empresa.upper()
        self.title = title.upper()

        # preparando cabeçalho
        styles = getSampleStyleSheet()
        self.header = [
            Paragraph(self.empresa, styles['Heading3']),
            Paragraph(self.title, styles['Heading5']),
        ]
        if header:
            _header = [Paragraph(h.upper(), styles['Heading6']) for h in header]
            self.header.extend(_header)

        self.columns_width = columns_width
        self.num_cols = len(columns_width)
        self.table_header = table_header
        self.table_data = table_data
        self.table_footer = table_footer
        self.buffer = buffer
        self.landscape = landscape
        self.pagesize = set_landscape(A4) if landscape else A4
        self.width, self.height = self.pagesize
        if not filename_logo:
            self.filename_logo = self.get_filename_image()
        else:
            self.filename_logo = filename_logo
        self.show_pages = show_pages
        self.report_type = report_type
        self.elements = []
        self.extra_tables = extra_tables

    def build(self):
        """
        Inicia a geração do relatório
        :return:
        """
        buffer = self.buffer
        doc = SimpleDocTemplate(
            buffer,
            rightMargin=inch / 6,
            leftMargin=inch / 6,
            topMargin=inch / 9,
            bottomMargin=inch / 4,
            pagesize=self.pagesize,
            title=self.title
        )

        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.

        image_side = Image(self.filename_logo, width=80, height=80)
        image_side.hAlign = 'LEFT'
        image_side.spaceAfter = 10
        self.elements.append(ImageAndFlowables(
            image_side,
            self.header,
            imageSide='left'
        ))

        self.switch_type(doc)

        if self.show_pages:
            if not self.landscape:
                doc.build(self.elements, canvasmaker=PaginadorPortrait)
            else:
                doc.build(self.elements, canvasmaker=PaginadorLandscape)
        else:
            doc.build(self.elements)

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def switch_type(self, doc):
        """
        Faz o swich te tipo de relatorio
        :param doc: Doc template
        :return:
        """
        if self.report_type == types.TABLE:
            self.build_table(doc)
        elif self.report_type == types.NORMAL:
            self.build_normal(doc)
        elif self.report_type == types.GRAPH:
            self.build_graph(doc)
        elif self.report_type == types.CUSTOM:
            self.build_custom(doc)
        else:
            pass

    def build_table(self, doc):
        """
        Gera uma tabela
        :param doc: Doc template
        :return:
        """
        # gerando lista com os dados do relatorio
        table_data = [
            self.table_header
        ]

        core_table = []

        _data = [[Paragraph(str(value), self.get_align(self.columns_width[index][1])) for index, value in enumerate(row)] for row in self.table_data]
        table_data.extend(_data)
        core_table.extend([Paragraph(''), Paragraph('')] + _data)

        # Estilo da tabela
        table_style = [
            ('BACKGROUND', (0, 0), (self.num_cols - 1, 0), HexColor(0x426B8E)),
            ('TEXTCOLOR', (0, 0), (self.num_cols - 1, 0), colors.white),
            ('ALIGN', (0, 0), (self.num_cols - 1, 0), 'CENTER'),
            ('INNERGRID', (0, 0), (-1, -1), 0.05, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2,),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOX', (0, 0), (-1, -1), 0.05, colors.black)
        ]
        if self.table_footer:
            table_data.append(self.table_footer)
            core_table.append(self.table_footer)
            table_style.append(('BACKGROUND', (0, -1), (self.num_cols - 1, -1), HexColor(0x426B8E)))
            table_style.append(('TEXTCOLOR', (0, -1), (self.num_cols - 1, -1), colors.white))
            # aplicando o alinhamento de cada coluna no footer
            for index, column in enumerate(self.columns_width):
                table_style.append(('ALIGN', (index, -1), (index, -1), column[1]))

        # Criando a tabela
        user_table = Table(table_data, colWidths=[(doc.width / 100.0) * w[0] for w in self.columns_width])
        user_table.setStyle(TableStyle(table_style))

        # criando core table
        self._core_table = Table(core_table, colWidths=[(doc.width / 100.0) * w[0] for w in self.columns_width])
        self._core_table.setStyle(TableStyle(table_style))

        self.elements.append(user_table)

        for ext_buider in self.extra_tables:
            ext_buider.build()
            self.elements.append(ext_buider._core_table)

    def build_normal(self, doc):
        """
        Gera uma relatorio com paragrafos
        :param doc: Doc template
        :return:
        """
        pass

    def build_graph(self, doc):
        """
        Gera um ou mais graficos
        :param doc: Doc template
        :return:
        """
        pass

    def build_custom(self, doc):
        """
        Gera um relatorio customizado
        :param doc: Doc template
        :return:
        """
        pass

    @staticmethod
    def get_filename_image():
        """
        Retorna a url da imagem da infog2 como padrão
        :return: a url
        """

        return 'https://cdn3.iconfinder.com/data/icons/meanicons-4/512/meanicons_60-128.png'

    @staticmethod
    def get_align(align):
        """
        Define o alinhamento da celula de acordo com o parametro
        :param align: Alinhamento
        :return: objeto de alinhamento
        """
        column_style_right = ParagraphStyle(name='Normal', fontName=_baseFontName, fontSize=8, leading=12,
                                            alignment=TA_RIGHT)
        column_style_left = ParagraphStyle(name='Normal', fontName=_baseFontName, fontSize=8, leading=12,
                                           alignment=TA_LEFT)
        column_style_center = ParagraphStyle(name='Normal', fontName=_baseFontName, fontSize=8, leading=12,
                                             alignment=TA_CENTER)

        if align == 'RIGHT':
            return column_style_right
        if align == 'CENTER':
            return column_style_center

        return column_style_left


class PaginadorPortrait(canvas.Canvas):
    """
    Classe para realizar a paginação
    """
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
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(200 * mm, 0 * mm + (0.2 * inch),
                             "Página %d de %d" % (self._pageNumber, page_count))


class PaginadorLandscape(canvas.Canvas):
    """
    Classe para realizar a paginação
    """
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
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(280 * mm, 0 * mm + (0.2 * inch),
                             "Página %d de %d" % (self._pageNumber, page_count))
