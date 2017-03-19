r"""Command-line tool to cropfaces

Usage::

    $ cropfaces image.jpg NEAR

"""
import sys
import cropfaces
import pkg_resources  # part of setuptools

HELP="""cropfaces, the Human JSON.

Usage:
  cropfaces [options]
  cropfaces [options] <input>
  cropfaces (-h | --help)
  cropfaces (-V | --version)

Options:
  -h --help     Show this screen.
  -j            Output as formatted JSON.
  -c            Output as JSON.
  -V --version  Show version.
""";

def showerr(msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")

def main():
    args = []
    for arg in sys.argv[1:]:
        if arg == '-h' or arg == '--help':
            showerr(HELP)
            return
        elif arg == '-j': format = 'json'
        elif arg == '-c': format = 'compact'
        elif arg == '-V' or arg == '--version':
            showerr('Hjson ' + pkg_resources.require("Hjson")[0].version)
            return

        elif arg[0] == '-':
            showerr(HELP)
            raise SystemExit('unknown option ' + arg)
        else:
            args.append(arg)

    cropFaces = cropfaces.CropFaces()
    output = cropFaces.crop1Head(sys.argv[1], None, sys.argv[2])
    print output

if __name__ == '__main__':
    main()
