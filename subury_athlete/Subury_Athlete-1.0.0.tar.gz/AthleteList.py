import os
os.chdir("D:\HeadFirstPython\char_6\hfpy_ch6_data")
def sanitize(listitem):
    if '-' in listitem:
        splitter='-'
    elif ':' in listitem:
        splitter=':'
    else:
        return(listitem)
    (min,secs)=listitem.split(splitter)
    return(min+"."+secs)
class Athlete(list):
    def __init__(self,Name,Dob=None,Times=[]):
        list.__init__([])
        self.Name=Name
        self.Dob=Dob
        self.extend(Times)
    def top3(self):
        return(sorted(set([sanitize(each) for each in self]))[0:3])
def min_3(the_list):
    new_list=[]
    for each in the_list:
        if each not in new_list:
            new_list.append(each)
    return new_list[0:3]
def infodata(filename):
    try:
        with open(filename) as file:
            data=file.readline()
            data=data.strip().split(",")
            return(Athlete(data.pop(0),data.pop(0),data))
    except IOError as ioerr:
        print("ErrorInfo:"+str(ioerr))
        return(None)

