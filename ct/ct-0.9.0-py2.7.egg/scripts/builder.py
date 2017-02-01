import subprocess, os
from cantools import config
from cantools.util import log, error, read, write

def nextQuote(text, lastIndex=0):
    z = i = text.find('"', lastIndex)
    while z > 0 and text[z-1] == "\\":
        z -= 1
    return ((i-z)%2 == 0) and i or nextQuote(text, i+1)

def encodestrings(text):
    start = nextQuote(text) + 1
    while start != 0:
        end = nextQuote(text, start)
        if end == -1:
            error("parse",
                "unclosed quote: character %s"%(start-1,),
                "this quote: %s"%(text[start:start+config.parse_error_segment_length],),
                text)
        word = ''.join(["\\%s"%(oct(ord(ch))[1:],) for ch in list(text[start:end])])
        if "\\134" not in word: # don't re-escape!
            text = text[:start] + word + text[end:]
        start = nextQuote(text, start + len(word) + 1) + 1
    return text

def processhtml(html, admin_ct_path=None):
    html = html.replace("{", "&#123").replace("}", "&#125").replace("</body>", "%s</body>"%(config.noscript,))
    firststart = start = end = html.find(config.js.flag)
    js = []
    while start != -1:
        start += config.js.offset
        end = html.find('"', start)
        if end == -1:
            error("no closing quote in this file: %s"%(html,))
        url = html[start:end]
        flag = "/%s"%(config.js.path,)
        if admin_ct_path:
            if url.startswith(flag):
                url = url.replace(flag, admin_ct_path)
            else:
                url = os.path.join(os.path.abspath(os.curdir), "dynamic", url[1:])
        elif url.startswith(flag):
            url = url[1:]
        js.append(url)
        start = html.find(config.js.flag, end)
    log("js: %s"%(js,), 1)
    if start == end:
        return html, ""
    return html[:firststart] + "{jsspot}" + html[end+config.js.endoffset:], js

def compress(html):
    log("compressing html", 1)
    newhtml = html.replace("\n", " ").replace("\t", " ")
    while "  " in newhtml:
        newhtml = newhtml.replace("  ", " ")
    newhtml = newhtml.replace("> <", "><")
    log("orig: %s. new: %s"%(len(html), len(newhtml)), 2)
    return newhtml

def bfiles(dirname, fnames):
    return [fname for fname in fnames if os.path.isfile(os.path.join(dirname, fname)) and fname != ".svn" and not fname.endswith("~") and not "_old." in fname]

def tryinit(iline, inits, prefixes):
    if iline not in inits:
        inits.add(iline)
        prefixes.append(iline)

def require(line, jspaths, block, inits, admin_ct_path=None):
    rline = line[12:-3]
    rsplit = rline.split(".")
    log("module %s"%(rline,), important=True)
    jspath = os.path.join(admin_ct_path or config.js.path, *rsplit) + ".js"
    log("path %s"%(jspath,))
    if jspath not in jspaths:
        prefixes = []
        fullp = "window"
        for rword in rsplit:
            if rword[0].isalpha():
                fullp = ".".join([fullp, rword])
            else:
                fullp = "%s[%s]"%(fullp, rword)
            tryinit("%s = %s || {}"%(fullp, fullp), inits, prefixes)
        pblock = ";".join(prefixes)
        if pblock:
            jspaths.append(pblock)
        block = block.replace(line, "%s;%s"%(pblock,
            processjs(jspath, jspaths, inits, admin_ct_path)), 1)
    return block

def processjs(path, jspaths, inits, admin_ct_path=None):
    block = read(path)
    for line in block.split("\n"):
        if line.startswith("CT.require(") and not line.endswith(", true);"):
            block = require(line, jspaths, block, inits, admin_ct_path)
    jspaths.append(path)
    return "%s;\n"%(block,)

def compilejs(js, admin_ct_path=None):
    jsblock = ""
    jspaths = []
    inits = set(["window.CT = window.CT || {}"]) # already initialized
    for p in js:
        jsblock += processjs(p, jspaths, inits, admin_ct_path)
    return jspaths, jsblock

def checkdir(p):
    if not os.path.isdir(p):
        log('making directory "%s"'%(p,), 1)
        os.mkdir(p)

def build(admin_ct_path, dirname, fnames):
    """
    This parses an html file, squishes together the javascript, scans
    through for dynamic imports (CT.require statements), injects modules
    wherever necessary, and sticks the result in a big <script> tag.
    """
    conf = admin_ct_path and config.build.admin or config.build.web
    for mode, compdir in conf.compiled.items():
        todir = dirname.replace(conf.dynamic, compdir)
        log("Target Directory: %s"%(todir,), important=True)
        checkdir(todir)
        for fname in bfiles(dirname, fnames):
            frompath = os.path.join(dirname, fname)
            topath = os.path.join(todir, fname)
            data = read(frompath)
            log('building: %s -> %s'%(frompath, topath), important=True)
            if "fonts" in dirname or not fname.endswith(".html"):
                log('copying non-html file', 1)
            else:
                txt, js = processhtml(data, admin_ct_path)
                if js:
                    jspaths, jsblock = compilejs(js, admin_ct_path)
                    if mode is "static":
                        log("static mode", 1)
                        js = '\n'.join([p.endswith("js") and '<script src="/%s"></script>'%(p,) or '<script>%s</script>'%(p,) for p in jspaths])
                    elif mode is "production":
                        log("production mode", 1)
                        txt = compress(txt)
                        jsb = jsblock.replace('"_encode": false,', '"_encode": true,').replace("CT.log._silent = false;", "CT.log._silent = true;")
                        if config.customscrambler:
                            jsb += '; CT.net.setScrambler("%s");'%(config.scrambler,)
                        from slimit import minify
                        js = "<script>%s</script>"%(minify(jsb, mangle=True),)
                    else:
                        error("invalid mode: %s"%(mode,))
                    data = txt.format(jsspot=js).replace("&#123", "{").replace("&#125", "}")
                else:
                    data = txt
            write(data, topath)
    for fname in [f for f in fnames if os.path.isdir(os.path.join(dirname, f))]:
        os.path.walk(os.path.join(dirname, fname), build, admin_ct_path)

if __name__ == "__main__":
    os.path.walk(config.build.web.dynamic, build, None)
