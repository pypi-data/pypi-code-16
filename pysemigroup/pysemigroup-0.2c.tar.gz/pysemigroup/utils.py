import os
import tempfile
import webbrowser
import threading
def view_graphviz(graphviz_str):
    file_dot = tempfile.mkstemp(prefix=".", suffix=".dot",dir=".")[1]
    file_gif = tempfile.mkstemp(prefix=".", suffix=".gif",dir=".")[1]
    f = open(file_dot,'w')
    f.write(graphviz_str)
    f.close()
    os.system('dot -Tgif %s -o %s; rm %s'%(file_dot,file_gif, file_dot))
    webbrowser.open(file_gif)
    timer = threading.Timer(3,delete_file,args=[file_gif])
    timer.start()
def delete_file(s):
     os.system('rm %s'% s)


