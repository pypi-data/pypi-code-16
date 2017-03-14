"""
xml-archive-to-pdf

Usage:
    xml-archive-to-pdf (-i <xml_file>) (-o <pdf_file>)
    xml-archive-to-pdf (-i <xml_file>) (-o <pdf_file>) -l <logo_file>
    xml-archive-to-pdf (-i <xml_file>) (-o <pdf_file>) -f <font_folder>
    xml-archive-to-pdf (-i <xml_file>) (-o <pdf_file>) -l <logo_file> -f <font_folder>

Options:
    -h --help  aide
    -i <xml_file>, --input <xml_file>
    -o <pdf_file>, --output <pdf_file>
    -l <logo_file>, --logo <logo_file>
    -f <font_folder>, --font <font_folder>
"""

from docopt import docopt
from xml_archive_to_pdf.utils import build_pdf
import sys


def main(args=None):
    try:
        if not args:
            args = docopt(__doc__)
        xml_file = args.get("--input")
        pdf_file = args.get("--output")
        logo_file = args.get("--logo")
        font_folder = args.get("--font")
        build_pdf(xml_file, pdf_file, logo_file, font_folder)
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
