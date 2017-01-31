#!/usr/bin/env python
from lxml import etree
import argparse

def prep(stg, ns="{http://www.topografix.com/GPX/1/1}"):
    """
    This modifies the namespace path thingy so it works. I'm a bit hazy on
    exactly what's happening here, but this works so I'm going with it for now.

    This function could probably dispensed with if I deal with the namespace
    correctly. I should read the [lxml
    documentation](http://lxml.de/tutorial.html) better and also refer to [this
    post](http://stackoverflow.com/questions/37964570/read-gpx-using-lxml-and-xpath).
    [This post](http://stackoverflow.com/questions/18071387/read-gpx-using-python-elementtree-register-namespace) seems even more on topic.
    """
    return ns + stg.replace("/","/"+ns)

def fix_tree(tree, metric_out=True):
    """
    gpx files downloaded from InsightGenesis use a bunch of non standard gpx
    tags. Of concern for me, they use `depth` instead of `ele`. That means that
    when I try to import the gpx file into QGIS, it loses the depth information.
    That's no good. This function copies the content of the depth tag to
    the`ele` tag.

    Parameters
    ----------
    tree : lxml.etree
        The `etree` object representing the gpx file to be fixed.

    Returns
    -------
    tree : lxml.etree
        The `etree` object with `depth` copied to `ele` tag.
    """
    root = tree.getroot()
    for tp in root.findall(prep('trk/trkseg/trkpt')):
        # Check that the depth is valid
        if tp.findtext(prep('depthvalid')) == 'T':
            # get the depth in feet
            depft = float(tp.findtext(prep('depth')))
            # convert the depth to meters and make it negative
            if metric_out:
                depm = -1.0 * depft / 3.2808
            else:
                # some ludite might want to stick with feet
                depm = depft
            # create an 'ele' child of the trkpt
            newel = etree.SubElement(tp, "ele")
            # set the depth
            newel.text = unicode(depm)
            # append the element
            tp.append(newel)
    return tree

def fix_gpx(infile, outfile, metric_out=True):
    """

    This function applies `fix_tree` to a gpx file (`infile`) and writes the results to `outfile`. If `metric_out` is `True` (default), depth will be converted from feet to meters.

    Parameters
    ----------
    infile : string
        Path to the input gpx file. This is assumed to have the `depth` and
        `depthvalid` tags of a file downloaded from
        http://insightgenesis.laketrax.com.
    outfile : string
        Path to the output gpx file.
    """
    tree = etree.parse(infile)
    newtree = fix_tree(tree, metric_out=metric_out)
    with open(outfile, 'w+') as nf:
        newtree.write(nf)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy the depth from the `depth` tag to the standard gpx `ele` tag. This will allow the gpx to be imported into GIS programs while retaining the depth information.')
    parser.add_argument('infile', help='The file that you would like to fix.')
    parser.add_argument('outfile', help='The corrected output file.')
    metric_parser = parser.add_mutually_exclusive_group(required=False)
    metric_parser.add_argument('--metric', dest='metric_output', action='store_true', help='Output depths in meters rather than feet. Metric output is the default because: science.')
    metric_parser.add_argument('--no-metric', dest='metric_output', action='store_false', help='Do not convert depths to meters.')
    parser.set_defaults(metric_output=True)
    args = parser.parse_args()

    fix_gpx(args.infile, args.outfile, metric_out=args.metric_output)
