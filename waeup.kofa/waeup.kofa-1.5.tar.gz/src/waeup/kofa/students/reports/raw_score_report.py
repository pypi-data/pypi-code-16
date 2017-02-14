## $Id: raw_score_report.py 14514 2017-02-08 07:39:08Z henrik $
##
## Copyright (C) 2013 Uli Fouquet & Henrik Bettermann
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
import grok
import textwrap
from zope.i18n import translate
from zope.catalog.interfaces import ICatalog
from zope.component import queryUtility, getUtility
from zope.interface import implementer, Interface, Attribute
from waeup.kofa.interfaces import (
    IKofaUtils,
    academic_sessions_vocab, registration_states_vocab)
from waeup.kofa.interfaces import MessageFactory as _
from waeup.kofa.reports import IReport
from waeup.kofa.browser.pdf import get_signature_tables
from waeup.kofa.students.vocabularies import StudyLevelSource
from waeup.kofa.students.reports.level_report import LevelReportGeneratorPage
from waeup.kofa.students.reports.student_statistics import (
    StudentStatisticsReportPDFView)

class IRawScoreReport(IReport):

    session = Attribute('Session to report')
    level = Attribute('Level to report')
    faccode = Attribute('Faculty to report')
    depcode = Attribute('Department to report')
    certcode = Attribute('Certificate to report')
    creation_dt_string = Attribute('Human readable report creation datetime')

def get_courses(faccode, depcode, certcode, session, level):
    """Method 1: Get certificate courses of a
    certain department/certificate at a certain level.
    """
    site = grok.getSite()
    course_codes = []
    department = site['faculties'][faccode][depcode]
    if certcode == 'all':
        for cert in department.certificates.values():
            for certcourse in cert.values():
                if certcourse.level == level:
                    course_codes.append(certcourse.getCourseCode())
    else:
        certificate = site['faculties'][faccode][depcode].certificates[certcode]
        for certcourse in certificate.values():
            if certcourse.level == level:
                course_codes.append(certcourse.getCourseCode())
    return course_codes

def get_students(faccode, depcode, certcode, session, level, course_codes):
    """Get students in a certain department/certificate who registered courses
    in a certain session at a certain level.

    Returns a list of student data tuples.
    """
    cat = queryUtility(ICatalog, name="students_catalog")
    if certcode == 'all':
        certcode = None
    result = cat.searchResults(
        depcode = (depcode, depcode), faccode = (faccode, faccode),
        certcode = (certcode, certcode)
        )
    table = []
    for stud in result:
        if not stud['studycourse'].has_key(str(level)):
            continue
        level_obj = stud['studycourse'][str(level)]
        if level_obj.level_session != session:
            continue
        scores = dict()
        for ticket in level_obj.values():
            if ticket.code in course_codes:
                if ticket.total_score is not None:
                    scores[ticket.code] = (ticket.total_score, ticket.grade)
                else:
                    scores[ticket.code] = ('Nil', '')
        fullname = textwrap.fill(stud.display_fullname, 26)
        line = (
                stud.matric_number,
                fullname,
                scores,
                )
        table.append(line)
    return sorted(table, key=lambda value:value[0])

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Table, Spacer
from reportlab.platypus.flowables import Flowable
from waeup.kofa.reports import IReport, IReportGenerator
from waeup.kofa.reports import Report
from waeup.kofa.browser.interfaces import IPDFCreator

STYLE = getSampleStyleSheet()

class TTR(Flowable): #TableTextRotate
    '''Rotates a text in a table cell.'''

    def __init__(self, text):
        Flowable.__init__(self)
        self.text=text

    def draw(self):
        canvas = self.canv
        canvas.rotate(25)
        canvas.drawString( 0, -1, self.text)

def tbl_data_to_table(data, course_codes):
    col_names = (
            #'Student Id',
            'S/N',
            'Matric No.',
            'Name',
            )
    catalog = getUtility(ICatalog, name='courses_catalog')
    for code in course_codes:
        course = list(catalog.searchResults(code=(code, code)))[0]
        col_names += (TTR('%s (%s)' % (code, course.credits)),)
    table = [col_names]
    sn = 1
    for line in data:
        scores = tuple()
        composed_line = (sn,) + line[:-1]
        for code in course_codes:
            result = line[-1].get(code)
            if not result:
                scores += ('N/R',)
            else:
                scores += ('%s%s' % (result[0], result[1]),)
        composed_line += scores
        table.append(composed_line)
        sn += 1
    return table

TABLE_STYLE = [
    ('FONT', (0,0), (-1,-1), 'Helvetica', 8),
    ('VALIGN', (0, 1), (-1,-1), 'TOP'),
    #('FONT', (0,0), (0,-1), 'Helvetica-Bold', 8), # 1st column
    ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 8), # 1st row
    #('FONT', (0,-1), (-1,-1), 'Helvetica-Bold', 8), # last row
    #('FONT', (-1,0), (-1,-1), 'Helvetica-Bold', 8), # last column
    ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
    ('ALIGN', (0,0), (0,-1), 'RIGHT'),
    #('ALIGN', (6,0), (6,-1), 'LEFT'),
    ('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
    ('BOX', (0,1), (-1,-1), 1, colors.black),
    ]

@implementer(IRawScoreReport)
class RawScoreReport(Report):
    data = None
    session = None
    level = None
    faccode = None
    depcode = None
    certcode = None

    note = ""
    signatures = None

    def __init__(self, faccode, depcode, certcode, session, level,
                 author='System'):
        super(RawScoreReport, self).__init__(
            args=[faccode, depcode, certcode, session, level],
                  kwargs={'author':author})
        site = grok.getSite()
        self.studylevelsource = StudyLevelSource().factory
        self.portal_language = getUtility(IKofaUtils).PORTAL_LANGUAGE
        self.session = academic_sessions_vocab.getTerm(session).title
        self.levelcode = level
        self.sessioncode = session
        self.faccode = faccode
        self.depcode = depcode
        self.certcode = certcode
        self.factitle = site['faculties'][faccode].longtitle
        self.deptitle = site['faculties'][faccode][depcode].longtitle
        if self.certcode == 'all':
            self.certtitle = translate(
                _('All Certificates'), 'waeup.kofa',
                target_language=self.portal_language)
            self.level = translate(
                self.studylevelsource.getTitle(None, int(level)),
                'waeup.kofa', target_language=self.portal_language)
        else:
            certificate = site[
                'faculties'][faccode][depcode].certificates[certcode]
            self.certtitle = certificate.longtitle
            self.level = translate(
                self.studylevelsource.getTitle(certificate, int(level)),
                'waeup.kofa', target_language=self.portal_language)
        self.author = author
        self.creation_dt_string = self.creation_dt.astimezone(
            getUtility(IKofaUtils).tzinfo).strftime("%Y-%m-%d %H:%M:%S %Z")
        self.past_levels = range(int(level/100)*100, 0, -100)
        self.course_codes = dict()
        self.data = dict()
        for level in self.past_levels:
            course_codes = get_courses(
                faccode, depcode, certcode, session, level)
            self.course_codes[level] = course_codes
            self.data[level] = get_students(
                faccode, depcode, certcode, session,
                self.levelcode, course_codes)

    def create_pdf(self, job_id):
        creator = getUtility(IPDFCreator, name='A3landscape')
        table_data = dict()
        for level in self.past_levels:
            table_data[level] = tbl_data_to_table(
                self.data[level], self.course_codes[level])
        col_widths = [1*cm, 4*cm, 5*cm] + [1*cm] * len(self.course_codes)
        pdf_data = [Paragraph('<b>%s - Report %s</b>'
                              % (self.creation_dt_string, job_id),
                              STYLE["Normal"]),
                    Spacer(1, 12),]
        pdf_data += [Paragraph(
                    translate(
                        '${a}<br />${b}<br />${c}<br />'
                        'Session: ${d}<br />Level: ${e}',
                        mapping = {'a':self.certtitle,
                                   'b':self.deptitle,
                                   'c':self.factitle,
                                   'd':self.session,
                                   'e':self.level,
                                   }),
                    STYLE["Normal"]),
                    ]

        for level in self.past_levels:
            pdf_data.append(Spacer(1, 20))
            pdf_data += [Paragraph('<b>Level %s Courses</b>' % level,
                        STYLE["Normal"]), Spacer(1, 20),]
            pdf_data += [
                Table(table_data[level],
                      style=TABLE_STYLE,
                      colWidths=col_widths)]
        doc_title = translate(_('Raw Score Report'))
        pdf_data.append(Spacer(1, 20))
        if self.signatures:
            signaturetables = get_signature_tables(
                self.signatures, landscape=True)
            pdf_data.append(signaturetables[0])

        pdf = creator.create_pdf(
            pdf_data, None, doc_title, self.author,
            doc_title + ' - %s -' % self.session,
            note=self.note
            )
        return pdf

@implementer(IReportGenerator)
class RawScoreReportGenerator(grok.GlobalUtility):

    title = _('RAW Score Report')
    grok.name('raw_score_report')

    def generate(self, site, faccode=None, depcode=None, certcode=None,
                 session=None, level=None, author=None):
        result = RawScoreReport(faccode=faccode, depcode=depcode,
            certcode=certcode, session=session, level=level, author=author)
        return result

###############################################################
## Browser related stuff
##
## XXX: move to local browser module
###############################################################
from waeup.kofa.browser.layout import KofaPage
from waeup.kofa.interfaces import academic_sessions_vocab
from waeup.kofa.reports import get_generators
from waeup.kofa.browser.breadcrumbs import Breadcrumb
grok.templatedir('browser_templates')
class RawScoreReportGeneratorPage(LevelReportGeneratorPage):

    grok.context(RawScoreReportGenerator)

    label = _('Create raw score report')

class RawScoreReportPDFView(StudentStatisticsReportPDFView):

    grok.context(IRawScoreReport)
    grok.name('pdf')
    grok.require('waeup.handleReports')
    prefix = 'RawScoreReport'

    def _filename(self):
        return 'RawScoreReport_rno%s_%s.pdf' % (
            self.context.__name__,
            self.context.creation_dt_string)

class RawScoreReportBreadcrumb(Breadcrumb):
    """A breadcrumb for reports.
    """
    grok.context(RawScoreReportGenerator)
    title = _(u'Raw Score Report')
    target = None