import os
import tempfile
import webbrowser
import threading
GraphVizExt = ["bmp",
"canon",
"dot",
"gv",
"xdot",
"xdot1.2",
"xdot1.4",
"cgimage",
"cmap",
"eps",
"exr",
"fig",
"gd",
"gd2",
"gif",
"gtk",
"ico",
"imap",
"cmapx",
"imap_np",
"cmapx_np",
"ismap",
"jp2",
"jpg",
"jpeg",
"jpe",
"json",
"json0",
"dot_json",
"xdot_json",
"pct",
"pict",
"pdf",
"pic",
"plain",
"plain-ext",
"png",
"pov",
"ps",
"ps2",
"psd",
"sgi",
"svg",
"svgz",
"tga",
"tif",
"tiff",
"tk",
"vml",
"vmlz",
"vrml",
"wbmp",
"webp",
"xlib",
"x11"]
def view_graphviz(graphviz_str,save_to_file=None, extension="svg"):
    file_dot = tempfile.mkstemp(prefix=".", suffix=".dot",dir=".")[1]
    if (save_to_file==None):
        file_svg = tempfile.mkstemp(prefix=".", suffix="."+extension,dir=".")[1]
    else:
        file_svg = save_to_file
        l = file_svg.split(".")
        extension = l[len(l)-1]
    if extension not in GraphVizExt:
        raise ValueError("Not a valid Graphviz output format")    
    f = open(file_dot,'w')
    f.write(graphviz_str)
    f.close()    
    os.system('dot -T'+extension+' %s -o %s; rm %s'%(file_dot,file_svg, file_dot))
    webbrowser.open(file_svg)
    if (save_to_file==None):
        timer = threading.Timer(3,delete_file,args=[file_svg])
        timer.start()
def delete_file(s):
     os.system('rm %s'% s)


