import time
import msvcrt as m
import os

def isint( value ):
    try:
        int( value )
        return True
    except ValueError:
        return False

def isstr( value ):
    return isinstance( value, str )

def islist( value ):
    return isinstance( value, list )
        
def isdiv( divident, divisor ):
    return divident % divisor == 0

def isprime( integer ):
    if not isInt( integer ):
        print( "PMOD ERROR: isPrime() requires an integer input for paramater 'integer'" )
        return "ERROR"
    for i in range( 2, round( integer / 2 ) + 2 ):
        if isDiv( integer, i ) or integer == 3:
            return False
    return True

def isnum( value ):
    try:
        float( value )
        return True
    except ValueError:
        return False

def wait( seconds ):
    time.sleep( seconds )

def pause( dispText="Press any key to continue..." ):
    print( dispText )
    m.getch()

def clear():
    os.system( 'cls' if os.name == 'nt' else 'clear' )

def returnmaster( object_in_class ):
    return object_in_class._nametowidget( object_in_class.winfo_parent() )


# CustomFile Commands
def fileWrite( filepath, text ):
    file = open( filepath, 'w' )
    file.write( str( text ) )
    file.close()

def fileAdd( filepath, text ):
    file = open( filepath, 'a' )
    file.write( str( text ) )
    file.close()

# #def fileRead(filepath, line):
# #    file = open(filepath, 'r')
# #    if isInt(line):
# #        for i in crange(1, line - 1):
# #            file.readline()
# #        return file.readline().strip()
# #    elif line == "all":
# #        return file.read()
# #    elif line == "listForm":
# #        return file.readlines()
# #    elif line == "yield":
# #        n = file.readline()
# #        while n != "":
# #            yield n.strip()
# #            n = file.readline()
# #    else:
# #        return None
# #    file.close()
    
# -CustomFileName.txt commands END-

if __name__ == '__main__':
    print( "Initializing ASIC(Artificial Super Intelligence-Conciousness) download..." )
