
#!/usr/bin/python
## write by qingluan 
# just a run file 

import tornado.ioloop
from tornado.ioloop import IOLoop
from .setting import  appication, port


def main():
    appication.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
    