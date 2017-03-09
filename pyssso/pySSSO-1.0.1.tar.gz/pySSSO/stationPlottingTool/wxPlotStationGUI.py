#!/usr/bin/env python

import os
import wx

class ExampleFrame(wx.Frame):
    

    
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Station Mapping Tool",
                          size=(300, 200))
                          
        self.stationArea   = 'Globe'
        self.mapBackground = 'Standard'
        
        self.InitUI()

    def InitUI(self):
        # Add a panel so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)

        bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_OTHER, (16, 16))
        titleIco = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        font = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
        
        title = wx.StaticText(self.panel, wx.ID_ANY, 'Interface for Selecting Map Options')
        title.SetFont(font)
        
        topSizer        = wx.BoxSizer(wx.VERTICAL)
        titleSizer      = wx.BoxSizer(wx.HORIZONTAL)
        fileNameSizer   = wx.BoxSizer(wx.HORIZONTAL)
        plotTitleSizer  = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer        = wx.BoxSizer(wx.HORIZONTAL)
        areaSizer       = wx.BoxSizer(wx.HORIZONTAL)
        backgdSizer     = wx.BoxSizer(wx.HORIZONTAL)

        # the edit control - one line version.
        #-------------------------------------

        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_OTHER, (16, 16))
        
        fileNameIco  = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        lbl_fileName = wx.StaticText(self.panel, label="Station file (full path):")
        self.txt_fileName = wx.TextCtrl(self.panel, wx.ID_FILE,'')
        self.Bind(wx.EVT_TEXT, self.getStationFileName, self.txt_fileName)

        plotTitleIco  = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp)
        lbl_plotTitle = wx.StaticText(self.panel, label="Plot Title:             ")
        self.txt_plotTitle = wx.TextCtrl(self.panel, wx.ID_ANY,'')
        self.Bind(wx.EVT_TEXT, self.getPlotTitle, self.txt_plotTitle)
        
        #------------
        # Radio Boxes
        #------------
        
        # Area
        areaList = ['Globe', 'US',
                     'North America','Central America', 'South America',
                     'Africa', 'Europe',
                     'Asia', 'Australia/Oceania']
        self.rb = wx.RadioBox(self.panel, label="Select your area of interest:",
                         pos=(20, 120), choices=areaList,  majorDimension=3,
                         style=wx.RA_SPECIFY_COLS)
        self.rb.Bind(wx.EVT_RADIOBOX, self.EvtArea, self.rb)

        # Map Background
        backgdList = ['Standard', 'Blue Marble',
            'Land-Sea Mask', 'Shaded Relief', 'Etopo',
            'Etopo & Land-Sea Mask']

        self.backgd = wx.RadioBox(self.panel, label="Select the map background:",
                           choices=backgdList,  majorDimension=3,
                           style=wx.RA_SPECIFY_COLS)
        self.backgd.Bind(wx.EVT_RADIOBOX, self.EvtMapBackgd, self.backgd)
        
        #---------------
        # Define Buttons
        #---------------
        verifyBtn = wx.Button(self.panel, wx.ID_ANY, 'Verify')
        runBtn    = wx.Button(self.panel, wx.ID_ANY, 'Run'   )
        cancelBtn = wx.Button(self.panel, wx.ID_ANY, 'Cancel')

        # Action on buttons
        #------------------
        self.Bind(wx.EVT_BUTTON, self.onVerify, verifyBtn)
        self.Bind(wx.EVT_BUTTON, self.onRun,       runBtn)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelBtn)

        # Sizers
        titleSizer.Add(titleIco, 0, wx.ALL, 5)
        titleSizer.Add(title, 0, wx.ALL, 5)

        fileNameSizer.Add(fileNameIco, 0, wx.ALL, 5)
        fileNameSizer.Add(lbl_fileName, 0, wx.ALL, 5)
        fileNameSizer.Add(self.txt_fileName, 1, wx.ALL|wx.EXPAND, 5)

        plotTitleSizer.Add(plotTitleIco, 0, wx.ALL, 5)
        plotTitleSizer.Add(lbl_plotTitle, 0, wx.ALL, 5)
        plotTitleSizer.Add(self.txt_plotTitle, 1, wx.ALL|wx.EXPAND, 5)

        areaSizer.Add(self.rb, 0, wx.ALL, 5)
        backgdSizer.Add(self.backgd, 0, wx.ALL, 5)

        btnSizer.Add(cancelBtn, 0, wx.ALL, 5)
        btnSizer.Add(verifyBtn, 0, wx.ALL, 5)
        btnSizer.Add(   runBtn, 0, wx.ALL, 5)

        topSizer.Add(titleSizer,     0, wx.CENTER)
        topSizer.Add(wx.StaticLine(self.panel,), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(fileNameSizer,  0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(plotTitleSizer, 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(areaSizer,      0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(backgdSizer,    0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        topSizer.Add(btnSizer,       0, wx.ALL|wx.CENTER, 5)

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)

        self.Centre()


    def getStationFileName(self, event):
        self.stationFileName = self.txt_fileName.GetValue()

    def getPlotTitle(self, event):
        self.plotTitle = self.txt_plotTitle.GetValue()

    def EvtArea(self, event):
        self.stationArea = self.rb.GetStringSelection()

    def EvtMapBackgd(self, event):
        self.mapBackground = self.backgd.GetStringSelection()

    def onRun(self, event):
        import os.path
        import plotStationClass as psc
        
        if (os.path.isfile(self.stationFileName)):
           print
           print "Submitting the scripts for plotting"
           
           #if (self.plotTitle == None):
           #   self.plotTitle = "Plotting stations over " + self.stationArea
           
           self.printFields()
      
           psc.stationMap(self.stationFileName,
                          self.stationArea,
                          self.plotTitle,
                          self.mapBackground)
    
           #self.closeProgram()
        else:
           messg = 'The station file you provided does not exist!'
           dial = wx.MessageDialog(None, messg, 'Do you want to try again?',
                                    wx.OK | wx.CANCEL | wx.ICON_QUESTION)
           ret = dial.ShowModal()
           dial.Destroy()
               
           if ret == wx.ID_OK:
              pass
           else:
              self.Destroy()


    def onVerify(self, event):
        self.printFields()

    def printFields(self):
        print
        print "     Station File: ", self.stationFileName
        print "       Plot Title: ", self.plotTitle
        print "        Plot area: ", self.stationArea
        print "    Map Backgroud: ", self.mapBackground
    
    
    def onCancel(self, event):
        dial = wx.MessageDialog(None, 'Are you sure to quit?', 'Question',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            
        ret = dial.ShowModal()
        dial.Destroy()
        
        if ret == wx.ID_YES:
            self.Destroy()
        else:
            pass

    def closeProgram(self):
        self.Destroy()

def main():
   app = wx.App(False)
   frame = ExampleFrame()
   frame.Show()
   app.MainLoop()

# Run the program
if __name__ == '__main__':
   main()



