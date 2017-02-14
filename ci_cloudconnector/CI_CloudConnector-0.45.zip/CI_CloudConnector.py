#remarks test
import threading , pip , CI_LC_BL, time

import sys, logging
import cpppo
from cpppo.server.enip import address, client

upgradeCounter = 0
serverVersion = ''
threadTimer = None
    
from threading import Timer
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def reloadLC():
    try:
        CI_LC_BL.ci_print('! About to reload', 'ERROR')
        CI_LC_BL.reboot()
        #reload(CI_LC_BL)
        #CI_LC_BL.initConfig()
    except Exception as inst:
        CI_LC_BL.handleError('Error in reload', inst)
        #print "Error reload " + str(inst)        
        #logging.warning('Error in reload :: ' + str(inst))
        
def upgradeLC(ver='', currentVer=''):
    try:
        if ver=='':
            print('! About to upgrade to latest version')
            CI_LC_BL.ci_print('! About to upgrade to latest version')
            pip.main(['install','--upgrade','CI_CloudConnector'])
        else:
            print('! About to upgrade to specific version'+ ver)
            CI_LC_BL.ci_print('! About to upgrade to specific version ' + ver)
            pip.main(['install','--force-reinstall','CI_CloudConnector=='+ver])
    except Exception as inst:
        CI_LC_BL.handleError('Error in reload', inst)
        #print "Error upgrade " + str(inst)        
        #logging.warning('Error in upgrade :: ' + str(inst))
    
def MainLoop():
    global serverVersion
    global upgradeCounter
    global threadTimer
    if threadTimer:
        threadTimer.stop()
    
    try:        
        CI_LC_BL.Main()        

        # get version and update if needed
        CI_LC_BL.getCloudVersion()
        localVer = str(CI_LC_BL.getLocalVersion())
        updateToVer=str(CI_LC_BL.getServerSugestedVersion())
        #to prevent upgrading to much in case of a problem we count upgrade attempts and stop when its too big, but if the version changes we try again
        if serverVersion != updateToVer:
            serverVersion = updateToVer
            upgradeCounter = 0

        CI_LC_BL.ci_print ("local ver=" + localVer)
        CI_LC_BL.ci_print ("server ver= " + updateToVer)

        if str(updateToVer)=='None':
            updateToVer=''
        if (bool(updateToVer!='') & bool(updateToVer!=localVer) & bool(upgradeCounter<10)):
            upgradeCounter = upgradeCounter + 1
            CI_LC_BL.ci_print('Local Version is different than server suggested version, start auto upgrade from:' + localVer + ' To:' + updateToVer + ' Upgrade count:'+str(upgradeCounter))
            upgradeLC(updateToVer, localVer)
            reloadLC()
    except Exception as inst:
        CI_LC_BL.ci_print ("Error MainLoop " + str(inst))

    if threadTimer:
        threadTimer.start()
        
def testTimer():
    global threadTimer
    threadTimer.stop()
    print '1'
    time.sleep(6)
    print '2'
    threadTimer.start()
    
def StartMainLoop():
    global threadTimer
    try:
        CI_LC_BL.ci_print("CI_CloudConnector Started")
        threadTimer = RepeatedTimer(5, MainLoop)
        #threadTimer = RepeatedTimer(5, test)
    except Exception as inst:
        CI_LC_BL.ci_print("Error MainLoopStart " + str(inst))
        
def showHelp():
    print ("==============================================")
    print ("CI_CloudConnector Version: " +  CI_LC_BL.getLocalVersion())
    print ('CI_CloudConnector.py :Start application')
    print ('CI_CloudConnector.py help   : display command line help')
    print ('CI_CloudConnector.py Start  : Start Main Loop')
    print ('CI_CloudConnector.py Config : UpdateConfig defenitions')
    print ("==============================================")
    print ('CI_CloudConnector.py getCloudVersion : check server suggected version and time')
    print ('CI_CloudConnector.py getCloudTags  : Get Tags defenition from Cloud and save into file')
    print ('CI_CloudConnector.py LocalDefTagsFiles : Show the tags saved in file')
    print ('CI_CloudConnector.py readModBusTags : Read Tags Fom Modbus and save to file')
    print ('CI_CloudConnector.py readEtherNetIP_Tags : Read Tags Fom EtehernatIP and save to file')
    print ('CI_CloudConnector.py handleAllValuesFiles : Send Values from all files to cloud')    
    print ('CI_CloudConnector.py TestMainLoopOnce : test main loop functionality one time')    
    print ("==============================================")

def args(argv):
    #print 'Argument List:', str(argv)
    #print 'Argument List:', str(len(argv))
    #if (len(sys.argv)==1):
    #    CI_LC_BL.MainLoopStart()
    if (len(argv)>1 and argv[1]=='help'):
        showHelp()
    if (len(argv)>1 and argv[1]=='Start'):
        StartMainLoop()
    if (len(argv)>1 and argv[1]=='Config'):
        CI_LC_BL.initConfig(True)
        
    if (len(argv)>1 and argv[1]=='getCloudTags'):
        token=''
        token = CI_LC_BL.getCloudToken()
        CI_LC_BL.getCloudTags(token)
    if (len(argv)>1 and argv[1]=='LocalDefTagsFiles'):
        tagsDef = CI_LC_BL.getTagsDefenitionFromFile()
        CI_LC_BL.printTags(tagsDef)
    if (len(argv)>1 and argv[1]=='readModBusTags'):
        tagsDef = getTagsDefenitionFromFile()
        #printTags(tagsDef)
        values = readModBusTags(tagsDef)
        printTagValues(values)
        saveValuesToFile(values,'')
    if (len(argv)>1 and argv[1]=='readEtherNetIP_Tags'):
        tagsDef = getTagsDefenitionFromFile()
        printTags(tagsDef)
        values = readEtherNetIP_Tags(tagsDef)
        printTagValues(values)
        saveValuesToFile(values,'')
    if (len(argv)>1 and argv[1]=='handleAllValuesFiles'):
        token=''
        token = CI_LC_BL.getCloudToken()
        CI_LC_BL.handleAllValuesFiles(token)
    if (len(argv)>1 and argv[1]=='TestMainLoopOnce'):
        MainLoop()
    if (len(argv)>1 and argv[1]=='upgradeLC'):
        upgradeLC()
    if (len(argv)>1 and argv[1]=='getCloudVersion'):
        CI_LC_BL.getCloudVersion()

def menu(option='help'):
    args(["",option])
    
#handle
#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)
#print 'Argument List:', str(sys.argv[1])
CI_LC_BL.initLog()
CI_LC_BL.createLibIfMissing()
CI_LC_BL.initConfig()

args(sys.argv)

#MainLoop()
    






