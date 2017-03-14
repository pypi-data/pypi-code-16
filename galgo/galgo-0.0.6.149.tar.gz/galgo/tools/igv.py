from __future__ import print_function, absolute_import
from argtools import command, argument
from collections import namedtuple
import os
from ..igv import IGVServer, IGVClient
import vcf


__SESSION_TMPL__ = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<Session {genome_attr} locus="{locus}" version="5">
    <Resources>
        {resources}
    </Resources>
    <Panel height="844" name="Panel1371449666544" width="{width}">
        {panel}
    </Panel>
    <Panel height="329" name="FeaturePanel" width="{width}">
        <Track altColor="0,0,178" autoScale="false" color="0,0,178" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10" id="Reference sequence" name="Reference sequence" sortable="false" visible="true"/>
        <Track altColor="0,0,178" autoScale="false" clazz="org.broad.igv.track.FeatureTrack" color="0,0,178" colorScale="ContinuousColorScale;0.0;297.0;255,255,255;0,0,178" displayMode="COLLAPSED" featureVisibilityWindow="-1" fontSize="10" height="35" id="hg19_genes" name="RefSeq Genes" renderer="BASIC_FEATURE" sortable="false" visible="true" windowFunction="count">
            <DataRange baseline="0.0" drawBaseline="true" flipAxis="false" maximum="297.0" minimum="0.0" type="LINEAR"/>
        </Track>
    </Panel>
    <PanelLayout dividerFractions="{dividerFractions}"/>
</Session>"""


@command.add_sub
@argument('-g', '--genome')
@argument('-l', '--locus', default='All')
@argument('files', nargs='*')
def igv_session(args):
    """
    """
    paths = []
    path_set = set()
    tracks = []
    for path in args.files:
        path = os.path.abspath(path)
        if path not in path_set:
            paths.append(path)
        if path.endswith('.bam'):
            name = os.path.basename(path)
            track = """\
<Track altColor="0,0,178" autoScale="true" color="175,175,175" displayMode="{displayMode}" featureVisibilityWindow="-1" fontSize="10" id="{id}" name="{name}" showReference="false" snpThreshold="{snpThreshold}" sortable="true" visible="true">
    <DataRange baseline="0.0" drawBaseline="true" flipAxis="false" maximum="60.0" minimum="0.0" type="LINEAR"/>
</Track>""".format(
                id=path + '_coverage',
                name=name + ' Coverage',
                displayMode='COLLAPSED',
                snpThreshold=0.2,
            )
            tracks.append(track)

        # default
        name = os.path.basename(path)
        track = """\
<Track altColor="0,0,178" autoScale="false" color="0,0,178" displayMode="{displayMode}" featureVisibilityWindow="-1" fontSize="10" id="{id}" name="{name}" showSpliceJunctions="false" sortable="true" visible="true">
        <RenderOptions colorByTag="" colorOption="{colorOption}" flagUnmappedPairs="false" groupByTag="" maxInsertSize="1000" minInsertSize="50" shadeBasesOption="{shadeBasesOption}" shadeCenters="true" showAllBases="false" sortByTag=""/>
</Track>""".format(
            id=path,
            name=name,
            displayMode='EXPANDED',
            colorOption='UNEXPECTED_PAIR',
            shadeBasesOption='QUALITY',
        )
        tracks.append(track)

    genome = args.genome
    if genome.endswith('.fa'):
        genome = os.path.abspath(genome)

    session = __SESSION_TMPL__.format(
            resources='\n'.join('<Resource path="{path}"></Resource>'.format(path=path) for path in paths),
            panel='\n'.join(tracks),
            genome_attr='genome="{0}"'.format(genome) if genome else '',
            locus=args.locus,
            width=2528,
            dividerFractions='0,0.7',  # TODO
            #dividerFractions='0.005046257359125316,0.7190916736753574',  # TODO
    )
    print (session)


@command.add_sub
@argument('feature', help='default is bed file')
@argument('-t', '--type', default=None, help='feature type')
@argument('-s', '--session')
@argument('-p', '--igv-port', default=60151, type=int)
@argument('-r', '--margin-ratio', default=.1, type=float)
@argument('-m', '--min-length', default=300, type=int)
def igv_links(args):
    """ Output html to jump region
    You may add session loading link by specify <session>

    BED
    BED with header
    VCF
    """
    session = os.path.abspath(args.session)
    Region = namedtuple('Region', 'contig start end')
    def iter_vcf(fname):
        with open(fname) as fp:
            reader = vcf.Reader(fp)
            header = ['contig', 'start', 'end', 'length', 'id', 'ref', 'alt', 'filter', 'info']
            yield header
            for rec in reader:
                start = rec.POS - 1
                end = rec.INFO['END'] if 'END' in rec.INFO \
                        else rec.POS + len(str(rec.REF)) - 1
                reg = Region(rec.CHROM, start, end)
                info = ' '.join('{0}={1}'.format(k, v) for k, v in rec.INFO.items())
                alt = ','.join(map(str, rec.ALT))
                row = [rec.CHROM, start, end, end - start, rec.ID, rec.REF, alt, ''.join(rec.FILTER), info]
                yield reg, row

    def iter_bed(fname):  # TODO how to handle with header
        with open(fname) as fp:
            row = next(fp).split('\t')
            if row[1].isdigit():
                # no header
                header = ['contig', 'start', 'end', 'length', 'name'] + list('col{0}'.format(i+1) for i in xrange(len(row) - 4))
                reg = Region(row[0], int(row[1]), int(row[2]))
                row = row[:2] + [reg.end - reg.start] + row[2:]
                yield header
                yield reg, row  # first line
            else:
                yield row  # header
            for row in fp:
                reg = Region(row[0], int(row[1]), int(row[2]))
                row = row[:2] + [reg.end - reg.start] + row[2:]
                yield reg, row

    its = {'bed': iter_bed, 'vcf': iter_vcf}  # TODO bed with head
    def get_iterable(fname):
        if args.type is not None:
            return its[args.type](fname)
        if fname.endswith('.vcf'):
            return its['vcf'](fname)
        if fname.endswith('.bed'):
            return its['bed'](fname)
        return its['bed'](fname)

    print ('''<html>''')
    print ('''<body>''')
    print ('''<p><a href="http://localhost:{igv_port}/load?file=file://{session}"> Load session </a></p>'''.format(igv_port=args.igv_port, session=session))
    print ('<table>')
    it = get_iterable(args.feature)
    header = next(it)
    print ('<thead>')
    print ('<tr>')
    print ('''<th>IGV link</th>''')
    for term in header:
        print ('<th>{0}</th>'.format(term))
    print ('</tr>')
    print ('</thead>')
    print ('<tbody>')
    for reg, row in it:
        length = reg.end - reg.start
        margin = int(length * args.margin_ratio)
        left = reg.start - margin
        right =  reg.end + margin
        diff = args.min_length - (right - left)
        if diff > 0:
            left -= int(diff / 2)
            right += int(diff / 2)
        locus = '{0}:{1}-{2}'.format(reg.contig, left, right)
        print ('<tr>')
        print ('''<td><a href="{link}">igv_link</a></td>'''.format(link='http://localhost:{igv_port}/goto?locus={locus}'.format(igv_port=args.igv_port, locus=locus)))
        for term in row:  # TODO html escape
            print ('<td>{0}</td>'.format(term))
        print ('</tr>')
    print ('</tbody>')
    print ('</table>')
    print ('''</body>''')
    print ('''</html>''')


@command.add_sub
@argument('files', nargs='+', help='URL or file path')
@argument.exclusive(
    argument('-l', '--loci', nargs='+'),
    argument('-L', '--loci-file'),
)
@argument('-P', '--paths', nargs='+')
@argument('-g', '--genome')
@argument('-p', '--port', type=int)
@argument('-o', '--outdir')
@argument('-m', '--view-mode', choices=['expand', 'collapse', 'squished'])
@argument('--view-as-pairs', action='store_true')
@argument('--height', type=int)
@argument('--run-server', action='store_true', help='Run IGV server during snapshot')
@argument('--no-reset', dest='reset_on_end', action='store_false', help='Reset IGV server status on end')
def igv_snapshot(args):
    """ Taking IGV snapshot
    """
    if not args.loci and not args.loci_file:
        logging.warning('Either of loci or loci_file is required')
        return (1)

    def iter_loci():
        if args.loci:
            for locus in args.loci:
                locus_name = locus.replace(':', '_').replace('/', '_') + '.png'
                path = os.path.join(args.outdir or os.curdir, locus_name)
                yield (locus, path)
        elif args.loci_file:
            with open(args.loci_file) as fp:
                for line in fp:
                    row = line.rstrip().split('\t')
                    locus = row[0]
                    locus_name = locus.replace(':', '_').replace('/', '_') + '.png'
                    path = os.path.join(args.outdir or os.curdir, locus_name)
                    yield (locus, path)

    def snapshot(igv):
        if args.genome:
            igv.genome(args.genome)
        if args.height:
            igv.set_height(args.height)
        for fn in args.files:
            igv.load(fn)
        if args.view_mode:
            getattr(igv, view_mode)()
        if args.view_as_pairs:
            igv.view_as_pairs()

        for locus, path in iter_loci():
            igv.goto(locus)
            igv.save(path)
        if args.reset_on_end:
            igv.new()

    if args.run_server:
        with IGVServer(port=args.port) as server, server.get_client() as igv:
            snapshot(igv)
    else:
        with IGVClient(port=args.port) as igv:
            snapshot(igv)


if __name__ == '__main__':
    command.run()
