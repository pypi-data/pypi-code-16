import parseJATS as parser
import json
import sys

def main(doc):
    soup = parser.parse_document(doc)
    print json.dumps(parser.authors_json(soup), indent=4)


if __name__ == '__main__':  # pragma: no cover
    main(sys.argv[1]) # pragma: no cover
