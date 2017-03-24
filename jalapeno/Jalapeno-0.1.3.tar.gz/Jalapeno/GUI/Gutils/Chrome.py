
def Browse(listen):

    from cefpython3 import cefpython as cef
    import platform
    import sys

    def check_versions():
        print("[hello_world.py] CEF Python {ver}".format(ver=cef.__version__))
        print("[hello_world.py] Python {ver} {arch}".format(
                ver=platform.python_version(), arch=platform.architecture()[0]))
        assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"

    
    check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    cef.Initialize()
    cef.CreateBrowserSync(url="https://127.0.0.1:5588")
    cef.MessageLoop()
    cef.Shutdown()

