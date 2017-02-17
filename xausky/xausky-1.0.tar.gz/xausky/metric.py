import time

def metric(tag):
    def tag_wrapper(func):
        print "[%s] init function[%s] metric"%(tag,func.__name__)
        def wrapper(*args):
            start = time.clock()
            result = func(*args)
            end = time.clock()
            print "[%s] this function[%s%s] called metric:%fs"%(tag,func.__name__,args,end-start)
            return result
        return wrapper
    return tag_wrapper
