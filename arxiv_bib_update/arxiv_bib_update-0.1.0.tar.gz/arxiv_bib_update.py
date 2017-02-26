from __future__ import print_function

import argparse
import bibtexparser
import ads
import os

__version__ = '0.1.0'

def is_preprint(adsurl):
    """
    Return whether the link is an arXiv preprint
    """
    return adsurl is not None and ('arXiv' in adsurl or 'astro.ph' in adsurl)

def main():
    
    desc = 'a simple tool to find out-of-date arXiv preprints, optionally updating and writing a new file'
    parser = argparse.ArgumentParser(description=desc)
    
    h = 'the input bib file to search through'
    parser.add_argument('bibfile', type=str, help=h)
    
    h = 'the output bib file to write; if not provided; any new entries will be writted to stdout'
    parser.add_argument('-o', '--output', type=str, help=h)
    
    h = "string specifying NASA ADS API token; see https://github.com/adsabs/adsabs-dev-api#access. "
    h += "The token can also be stored in ~/.ads/dev_key for repeated use"
    parser.add_argument('-t', '--token', type=str, help=h)
    
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
        if is_preprint(adsurl):
            preprints.append(i)
    
    # sort from largest to smallest
    preprints = sorted(preprints, reverse=True)
    print("found %d possibly out-of-date preprints..." %len(preprints))   

    # get the relevant info from ADS
    updated = []
    for i in preprints:
        r = refs.entries[i]
        
        # the arxiv id
        arxiv_id = r['adsurl'].split('abs/')[-1]
        
        # query for the bibcode
        q = ads.SearchQuery(q="arxiv:%s" %arxiv_id, fl=['bibcode'])
        
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
            if not is_preprint(new_ref.get('adsurl', None)):
                updated.append(new_ref['ID'])
                print("'%s' entry found to be out-of-date" %r['ID'])
                
                # remove old entry
                refs.entries.pop(i)
                
                # add new entry
                refs.entries.append(new_ref)

    # write output file
    if len(updated):
        
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