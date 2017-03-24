from multiprocessing import Process
import multiprocessing

def Browse():
    from cefpython3 import cefpython as cef
    import platform
    import sys

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)
    try:
        
        #sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
        cef.Initialize()
        cef.CreateBrowserSync(url="https://127.0.0.1:5588")
        cef.MessageLoop()
        cef.Shutdown()
    except Exception:
        logger.exception('whoopsie')


p = Process(target=Browse)
p.start()
p.join()
