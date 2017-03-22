import os
import re

from pprint import pprint
from stdplus import readfile

class SshConfigBlock(list):
    def __init__(self,line,lineNumber):
        list.__init__(self)
        self.line = line
        self.lineNumber = lineNumber

    def __str__(self):
        return "{}{}{}".format(self.line,"\n" if len(self) > 0 else "","\n".join(x.__repr__() for x in self) )

    def __repr__(self):
        return "{}:<{}>{}{}".format(self.lineNumber,self.line,"\n" if len(self) > 0 else "","\n".join(x.__repr__() for x in self) )

class SshConfig(SshConfigBlock):
    def __init__(self):
        SshConfigBlock.__init__(self,'',0)
        self.hosts = {}
    def __str__(self):
        return "\n".join(x.__repr__() for x in self)
    def __repr__(self):
        return "\n".join(x.__repr__() for x in self)

class WithSettings(SshConfigBlock):
    def __init__(self,line,lineNumber):
        SshConfigBlock.__init__(self,line,lineNumber)
        self.settings = {}
    def addSetting(self,setting):
        if not setting.name in self.settings:
            self.settings[setting.name] = []
        self.settings[setting.name].append(setting)
        
class Host(WithSettings):
    def __init__(self,line,lineNumber):
        WithSettings.__init__(self,line,lineNumber)
        m = re.search('^.*Host[ \t]+([^#]*)(#.*)*',line)
        self.name = m.group(1)

class Comment(SshConfigBlock):
    pass

class Match(WithSettings):
    pass

class Setting(SshConfigBlock):
    def __init__(self,line,lineNumber):
        SshConfigBlock.__init__(self,line,lineNumber)
        m = re.search('^[ \t]*([A-Za-z_]*)[ \t]+([^#]*)(#.*)*',line)
        self.name = m.group(1)
        self.value = m.group(2)
        self.comment = m.group(3)

def parseSshConfig(contents):
    lines = contents.split('\n')
    lineNumber = 0
    rootBlock = SshConfig()
    currentBlock = rootBlock
    for line in lines:
        lineNumber += 1
        if 0 == len(line.strip()) or line.startswith('#'):
            currentBlock.append(Comment(line,lineNumber))
        elif line.strip().startswith('Host '):
            currentBlock = Host(line,lineNumber)
            rootBlock.append(currentBlock)
            rootBlock.hosts[currentBlock.name] = currentBlock
        elif line.strip().startswith('Match '):
            currentBlock = Match(line,lineNumber)
            rootBlock.append(currentBlock)
        else:
            setting = Setting(line,lineNumber)
            currentBlock.append(setting)
            if isinstance(currentBlock,Host) or isinstance(currentBlock,Match):
                currentBlock.addSetting(setting)
            
    return rootBlock

def readSshConfig(path=os.path.expanduser('~/.ssh/config')):
    config = readfile(path)
    return parseSshConfig(config)

