from warcio.bufferedreaders import DecompressingBufferedReader
from warcio.archiveiterator import ArchiveIterator
from warcio.recordloader import ArcWarcRecordLoader, ArcWarcRecord
from warcio.warcwriter import WARCWriter

import sys

def main():
    if len(sys.argv) > 1:
        stream = open(sys.argv[1], 'rb')
    else:
        print('Must specify input warc to compress')
        return

    if len(sys.argv) > 2:
        out = open(sys.argv[2], 'wb')
        close_out = True
    else:
        out = sys.stdout
        close_out = False
        if hasattr(out, 'buffer'):
            out = out.buffer


    writer = WARCWriter(filebuf=out, gzip=True)

    arciterator = ArchiveIterator(stream,
                                  no_record_parse=True,
                                  arc2warc=True,
                                  verify_http=False)

    for record in arciterator:
        writer.write_record(record)


    stream.close()

    if close_out:
        out.close()


main()


