from __future__ import print_function

import argparse
import bibtexparser
import ads
import os
import warnings
import re

__version__ = "0.1.1"

def make_arxiv_patterns():
    """
    Make the regular expressions for matching arXiv IDs
    """
    toret = [re.compile("[0-9]{4}.[0-9]{4}")] # default XXXX.XXXX format
    valid_names = ['astro-ph', 'cond-mat', 'gr-qc', 'hep-ex', 'hep-lat', 
                  'hep-ph', 'hep-th', 'math-ph', 'nlin', 'nucl-ex', 'nucl-th',
                  'physics', 'quant-ph']
    
    toret += [re.compile("%s/[0-9]{7}" %name) for name in valid_names]
    return toret
    
ARXIV_PATTERNS = make_arxiv_patterns()


def is_preprint(r):
    """
    Return whether the link is an arXiv preprint
    """
    ans = False
    
    # check the journal
    journal = r.get('journal', None)
    if journal is not None:
        if 'arxiv' in r['journal'].lower():
            ans = True
    else:
        return True
            
    # check the ads url
    adsurl = r.get('adsurl', None)
    if adsurl is not None:
       if ('arxiv' in adsurl.lower() or 'astro.ph' in adsurl):
           ans = True
        
    return ans

def main():
    
    desc = 'a simple tool to find out-of-date arXiv preprints, optionally updating and writing a new file'
    parser = argparse.ArgumentParser(description=desc)
    
    h = 'the input bib file to search through'
    parser.add_argument('bibfile', type=str, help=h)
    
    h = 'do a dry run, simply printing out all of the out-of-date references'
    parser.add_argument('--dry-run', '-n', action='store_true', help=h)
    
    h = 'the output bib file to write; if not provided; any new entries will be writted to stdout'
    parser.add_argument('-o', '--output', type=str, help=h)
    
    h = "string specifying NASA ADS API token; see https://github.com/adsabs/adsabs-dev-api#access. "
    h += "The token can also be stored in ~/.ads/dev_key for repeated use"
    parser.add_argument('-t', '--token', type=str, help=h)
    
    h = 'whether to use verbose output'
    parser.add_argument('-v', '--verbose', action='store_true', help=h)
    
    ns = parser.parse_args()
    
    # set the token
    if ns.token is not None:
        os.environ['ADS_DEV_KEY'] = ns.token
        
    # parse the bib file
    with open(ns.bibfile, 'r') as ff:
        refs = bibtexparser.load(ff)
        
    # the indices of pre-prints
    preprints = []
    for i, r in enumerate(refs.entries):
        adsurl = r.get('adsurl', None) 
        if is_preprint(r):
            preprints.append(i)
        elif ns.verbose:
            print("entry '%s' appears to be a published work" %(r['ID']))
    
    # sort from largest to smallest
    preprints = sorted(preprints, reverse=True)
    args = (len(preprints), len(refs.entries))
    print("%d out of %d references possibly out-of-date..." % args)   

    # get the relevant info from ADS
    updated = []
    for i in preprints:
        r = refs.entries[i]
        arxiv_id = None
        
        # try to match the pattern
        for field in r:
            for pattern in ARXIV_PATTERNS:
                 matches = pattern.search(r[field])
                 if matches:
                     arxiv_id = matches.group(0)
                     break
        
        # check ads url too
        if arxiv_id is None and 'adsurl' in r and 'abs/' in r['adsurl']:
            arxiv_id = r['adsurl'].split('abs/')[-1]
        
        # skip this one and warn!
        if arxiv_id is None:
            warnings.warn("cannot check entry '%s'; please add 'eprint' or proper 'adsurl' fields" %r['ID'])
            continue
        
        # query for the bibcode
        try:
            q = ads.SearchQuery(q="arxiv:%s" %arxiv_id, fl=['bibcode'])
        except:
            raise ValueError("syntax error in bib file; check 'eprint' and 'adsurl' fields for '%s'" %r['ID'])
        
        # check for token
        if q.token is None:
            raise RuntimeError("no ADS API token found; cannot query the ADS database. "
                               "See https://github.com/adsabs/adsabs-dev-api#access")
        
        # process each paper
        for paper in q:
            
            # get the bibtex
            bibquery = ads.ExportQuery(paper.bibcode)
            bibtex = bibquery.execute()
            
            # new ref entry
            new_ref = bibtexparser.loads(bibtex).entries[0]
            
            # update if published
            if not is_preprint(new_ref):
                updated.append(new_ref['ID'])
                print("'%s' entry found to be out-of-date" %r['ID'])
                
                # remove old entry
                refs.entries.pop(i)
                
                # add new entry
                refs.entries.append(new_ref)

    # write output file
    if len(updated) and not ns.dry_run:
        
        writer = bibtexparser.bwriter.BibTexWriter()
        if ns.output is not None:
            with open(ns.output, 'w') as ff:
                ff.write(writer.write(refs))
        else:
            # only print out the new ones
            indices = [i for i, ref in enumerate(refs.entries) if ref['ID'] in updated]
            refs.entries = [refs.entries[i] for i in indices]
            print(writer.write(refs))
        

if __name__ == '__main__':
    main()
