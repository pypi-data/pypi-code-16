"""
Class OWTextableIntersect
Copyright 2012-2016 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This file is part of the Orange-Textable package v2.0.

Orange-Textable v2.0 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange-Textable v2.0 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange-Textable v2.0. If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = '0.15.0'

"""
<name>Intersect</name>
<description>In-/exclude segments based on another segmentation</description>
<icon>icons/Intersect.png</icon>
<priority>4004</priority>
"""

import LTTL.Segmenter as Segmenter
from LTTL.Segmentation import Segmentation

from TextableUtils import *

from Orange.OrangeWidgets.OWWidget import *
import OWGUI


class OWTextableIntersect(OWWidget):
    """Orange widget for segment in-/exclusion based on other segmentation"""

    contextHandlers = {
        '': SegmentationListContextHandler(
            '', [
                ContextInputListField('segmentations'),
                ContextInputIndex('source'),
                ContextInputIndex('filtering'),
                'sourceAnnotationKey',
                'filteringAnnotationKey',
            ]
        )
    }

    settingsList = [
        'mode',
        'copyAnnotations',
        'autoSend',
        'autoNumber',
        'autoNumberKey',
        'displayAdvancedSettings',
        'uuid',
    ]

    def __init__(self, parent=None, signalManager=None):

        OWWidget.__init__(
            self,
            parent,
            signalManager,
            wantMainArea=0,
            wantStateInfoWidget=0,
        )

        # Input and output channels...
        self.inputs = [('Segmentation', Segmentation, self.inputData, Multiple)]
        self.outputs = [
            ('Selected data', Segmentation, Default),
            ('Discarded data', Segmentation)
        ]

        # Settings...
        self.copyAnnotations = True
        self.autoSend = False
        self.mode = u'Include'
        self.autoNumber = False
        self.autoNumberKey = u'num'
        self.displayAdvancedSettings = False
        self.uuid = None
        self.loadSettings()
        self.uuid = getWidgetUuid(self)

        # Other attributes...
        self.segmentations = list()
        self.source = None
        self.sourceAnnotationKey = None
        self.filtering = None
        self.filteringAnnotationKey = None
        self.settingsRestored = False
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )
        self.advancedSettings = AdvancedSettings(
            widget=self.controlArea,
            master=self,
            callback=self.sendButton.settingsChanged,
        )

        # GUI...

        # TODO: update docs to match removal of source annotation from basic

        self.advancedSettings.draw()

        # Intersect box
        self.intersectBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Intersect',
            orientation='vertical',
        )
        self.modeCombo = OWGUI.comboBox(
            widget=self.intersectBox,
            master=self,
            value='mode',
            sendSelectedValue=True,
            items=[u'Include', u'Exclude'],
            orientation='horizontal',
            label=u'Mode:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Specify whether source segments whose type is\n"
                u"present in the filter segmentation should be\n"
                u"included in or excluded from the output\n"
                u"segmentation."
            ),
        )
        self.modeCombo.setMinimumWidth(140)
        OWGUI.separator(widget=self.intersectBox, height=3)
        self.sourceCombo = OWGUI.comboBox(
            widget=self.intersectBox,
            master=self,
            value='source',
            orientation='horizontal',
            label=u'Source segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation from which a subset of segments\n"
                u"will be selected to build the output segmentation."
            ),
        )
        OWGUI.separator(widget=self.intersectBox, height=3)
        self.sourceAnnotationCombo = OWGUI.comboBox(
            widget=self.intersectBox,
            master=self,
            value='sourceAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Source annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether source segments will be selected\n"
                u"based on annotation values corresponding to a\n"
                u"specific annotation key or rather on their content\n"
                u"(value 'none')."
            ),
        )
        OWGUI.separator(widget=self.intersectBox, height=3)
        self.filteringCombo = OWGUI.comboBox(
            widget=self.intersectBox,
            master=self,
            value='filtering',
            orientation='horizontal',
            label=u'Filter segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose types will be used to\n"
                u"include source segments in (or exclude them from)\n"
                u"the output segmentation."
            ),
        )
        OWGUI.separator(widget=self.intersectBox, height=3)
        self.filteringAnnotationCombo = OWGUI.comboBox(
            widget=self.intersectBox,
            master=self,
            value='filteringAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Filter annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether filter segment types are based\n"
                u"on annotation values corresponding to a specific\n"
                u"annotation key or rather on segment content\n"
                u"(value 'none')."
            ),
        )
        OWGUI.separator(widget=self.intersectBox, height=3)
        self.advancedSettings.advancedWidgets.append(self.intersectBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Options box...
        optionsBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
        )
        optionsBoxLine2 = OWGUI.widgetBox(
            widget=optionsBox,
            box=False,
            orientation='horizontal',
            addSpace=True,
        )
        OWGUI.checkBox(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumber',
            label=u'Auto-number with key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotate output segments with increasing numeric\n"
                u"indices."
            ),
        )
        self.autoNumberKeyLineEdit = OWGUI.lineEdit(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumberKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for output segment auto-numbering."
            ),
        )
        OWGUI.checkBox(
            widget=optionsBox,
            master=self,
            value='copyAnnotations',
            label=u'Copy annotations',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Copy all annotations from input to output segments."
            ),
        )
        OWGUI.separator(widget=optionsBox, height=2)
        self.advancedSettings.advancedWidgets.append(optionsBox)
        self.advancedSettings.advancedWidgetsAppendSeparator()

        # Basic intersect box
        self.basicIntersectBox = OWGUI.widgetBox(
            widget=self.controlArea,
            box=u'Intersect',
            orientation='vertical',
        )
        self.basicModeCombo = OWGUI.comboBox(
            widget=self.basicIntersectBox,
            master=self,
            value='mode',
            sendSelectedValue=True,
            items=[u'Include', u'Exclude'],
            orientation='horizontal',
            label=u'Mode:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Specify whether source segments whose type is\n"
                u"present in the filter segmentation should be\n"
                u"included in or excluded from the output\n"
                u"segmentation."
            ),
        )
        self.basicModeCombo.setMinimumWidth(140)
        OWGUI.separator(widget=self.basicIntersectBox, height=3)
        self.basicSourceCombo = OWGUI.comboBox(
            widget=self.basicIntersectBox,
            master=self,
            value='source',
            orientation='horizontal',
            label=u'Source segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation from which a subset of segments\n"
                u"will be selected to build the output segmentation."
            ),
        )
        OWGUI.separator(widget=self.basicIntersectBox, height=3)
        self.basicFilteringCombo = OWGUI.comboBox(
            widget=self.basicIntersectBox,
            master=self,
            value='filtering',
            orientation='horizontal',
            label=u'Filter segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose types will be used to\n"
                u"include source segments in (or exclude them from)\n"
                u"the output segmentation."
            ),
        )
        OWGUI.separator(widget=self.basicIntersectBox, height=3)
        self.advancedSettings.basicWidgets.append(self.basicIntersectBox)
        self.advancedSettings.basicWidgetsAppendSeparator()

        OWGUI.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()
        self.adjustSizeWithTimer()

    def sendData(self):

        """(Have LTTL.Segmenter) perform the actual filtering"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Selected data', None, self)
            self.send('Discarded data', None, self)
            return

        # TODO: remove message 'No label was provided.' from docs

        # Source and filtering parameter...
        source = self.segmentations[self.source][1]
        filtering = self.segmentations[self.filtering][1]
        if self.displayAdvancedSettings:
            source_annotation_key = self.sourceAnnotationKey or None
            if self.sourceAnnotationKey == u'(none)':
                source_annotation_key = None
            filtering_annotation_key = self.filteringAnnotationKey or None
            if filtering_annotation_key == u'(none)':
                filtering_annotation_key = None
        else:
            source_annotation_key = None
            filtering_annotation_key = None

        # Check that autoNumberKey is not empty (if necessary)...
        if self.displayAdvancedSettings and self.autoNumber:
            if self.autoNumberKey:
                autoNumberKey = self.autoNumberKey
                num_iterations = 2 * len(source['segmentation'])
            else:
                self.infoBox.setText(
                    u'Please enter an annotation key for auto-numbering.',
                    'warning'
                )
                self.send('Selected data', None, self)
                self.send('Discarded data', None, self)
                return
        else:
            autoNumberKey = None
            num_iterations = len(source)

        # Basic settings...
        if self.displayAdvancedSettings:
            copyAnnotations = self.copyAnnotations
        else:
            copyAnnotations = True

        # Perform filtering...
        progressBar = OWGUI.ProgressBar(
            self,
            iterations=num_iterations
        )
        (filtered_data, discarded_data) = Segmenter.intersect(
            source=source,
            source_annotation_key=source_annotation_key,
            filtering=filtering,
            filtering_annotation_key=filtering_annotation_key,
            mode=self.mode.lower(),
            label=self.captionTitle,
            copy_annotations=self.copyAnnotations,
            auto_number_as=autoNumberKey,
            progress_callback=progressBar.advance,
        )
        progressBar.finish()
        message = u'%i segment@p sent to output.' % len(filtered_data)
        message = pluralize(message, len(filtered_data))
        self.infoBox.setText(message)

        self.send('Selected data', filtered_data, self)
        self.send('Discarded data', discarded_data, self)
        self.sendButton.resetSettingsChangedFlag()

    def inputData(self, newItem, newId=None):
        """Process incoming data."""
        self.closeContext()
        updateMultipleInputs(
            self.segmentations,
            newItem,
            newId,
            self.onInputRemoval
        )
        self.infoBox.inputChanged()
        self.updateGUI()

    def onInputRemoval(self, index):
        """Handle removal of input with given index"""
        if index < self.source:
            self.source -= 1
        elif index == self.source \
                and self.source == len(self.segmentations) - 1:
            self.source -= 1
            if self.source < 0:
                self.source = None
        if index < self.filtering:
            self.filtering -= 1
        elif index == self.filtering \
                and self.filtering == len(self.segmentations) - 1:
            self.filtering -= 1
            if self.filtering < 0:
                self.filtering = None

    def updateGUI(self):
        """Update GUI state"""
        if self.displayAdvancedSettings:
            sourceCombo = self.sourceCombo
            filteringCombo = self.filteringCombo
            intersectBox = self.intersectBox
        else:
            sourceCombo = self.basicSourceCombo
            filteringCombo = self.basicFilteringCombo
            intersectBox = self.basicIntersectBox
        sourceCombo.clear()
        self.sourceAnnotationCombo.clear()
        self.sourceAnnotationCombo.addItem(u'(none)')
        self.advancedSettings.setVisible(self.displayAdvancedSettings)
        if len(self.segmentations) == 0:
            self.source = None
            self.sourceAnnotationKey = u''
            intersectBox.setDisabled(True)
            self.adjustSize()
            return
        else:
            if len(self.segmentations) == 1:
                self.source = 0
            for segmentation in self.segmentations:
                sourceCombo.addItem(segmentation[1].label)
            self.source = self.source
            sourceAnnotationKeys \
                = self.segmentations[self.source][1].get_annotation_keys()
            for k in sourceAnnotationKeys:
                self.sourceAnnotationCombo.addItem(k)
            if self.sourceAnnotationKey not in sourceAnnotationKeys:
                self.sourceAnnotationKey = u'(none)'
            self.sourceAnnotationKey = self.sourceAnnotationKey
            intersectBox.setDisabled(False)
        self.autoNumberKeyLineEdit.setDisabled(not self.autoNumber)
        filteringCombo.clear()
        for index in range(len(self.segmentations)):
            filteringCombo.addItem(self.segmentations[index][1].label)
        self.filtering = self.filtering or 0
        segmentation = self.segmentations[self.filtering]
        if self.displayAdvancedSettings:
            self.filteringAnnotationCombo.clear()
            self.filteringAnnotationCombo.addItem(u'(none)')
            filteringAnnotationKeys = segmentation[1].get_annotation_keys()
            for key in filteringAnnotationKeys:
                self.filteringAnnotationCombo.addItem(key)
            if self.filteringAnnotationKey not in filteringAnnotationKeys:
                self.filteringAnnotationKey = u'(none)'
            self.filteringAnnotationKey = self.filteringAnnotationKey
        self.adjustSize()
        self.adjustSizeWithTimer()

    def adjustSizeWithTimer(self):
        qApp.processEvents()
        QTimer.singleShot(50, self.adjustSize)

    def setCaption(self, title):
        if 'captionTitle' in dir(self) and title != 'Orange Widget':
            OWWidget.setCaption(self, title)
            self.sendButton.settingsChanged()
        else:
            OWWidget.setCaption(self, title)

    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
        self.openContext("", self.segmentations)
        self.updateGUI()
        self.sendButton.sendIf()

    def getSettings(self, *args, **kwargs):
        settings = OWWidget.getSettings(self, *args, **kwargs)
        settings["settingsDataVersion"] = __version__.split('.')[:2]
        return settings

    def setSettings(self, settings):
        if settings.get("settingsDataVersion", None) \
                == __version__.split('.')[:2]:
            settings = settings.copy()
            del settings["settingsDataVersion"]
            OWWidget.setSettings(self, settings)


if __name__ == '__main__':
    from LTTL.Input import Input

    appl = QApplication(sys.argv)
    ow = OWTextableIntersect()
    seg1 = Input(u'hello world', 'text')
    seg2 = Segmenter.tokenize(
        seg1,
        [
            (re.compile(r'hello'), u'tokenize', {'tag': 'interj'}),
            (re.compile(r'world'), u'tokenize', {'tag': 'noun'}),
        ],
        label='words',
    )
    seg3 = Segmenter.tokenize(
        seg2,
        [(re.compile(r'[aeiou]'), u'tokenize')],
        label='V'
    )
    seg4 = Segmenter.tokenize(
        seg2,
        [(re.compile(r'[hlwrdc]'), u'tokenize')],
        label='C'
    )
    seg5 = Segmenter.tokenize(
        seg2,
        [(re.compile(r' '), u'tokenize')],
        label='S'
    )
    seg6 = Segmenter.concatenate(
        [seg3, seg4, seg5],
        import_labels_as='category',
        label='chars',
        sort=True,
        merge_duplicates=True,
    )
    seg7 = Segmenter.tokenize(
        seg6,
        [(re.compile(r'l'), u'tokenize')],
        label='pivot'
    )
    ow.inputData(seg2, 1)
    ow.inputData(seg6, 2)
    ow.inputData(seg7, 3)
    ow.show()
    appl.exec_()
    ow.saveSettings()
