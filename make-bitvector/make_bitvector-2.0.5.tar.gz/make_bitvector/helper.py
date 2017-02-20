#--------------------- Helper functions for parsing MD string and converting positions to quality ------------------------------------
import pysam
import numpy as np
import pandas as pd
import multiprocessing
import time 
from alignedRead import Read

def parse_read(read, ref_trim, ref_lengths, use_deletions, quals):    
    md = read.get_tag("MD")  
    muts, dels = get_positions(md, use_deletions)
    # get list of absolute mutations positions 
    mutation_list = [e[1] + read.reference_start for e in muts]

    if quals:
        # take quality scores into account; return list of absolute positions with insufficient quality
        invalid_pos = np.where(combine_quals(read, dels, use_deletions) < 20)[0] + read.reference_start

    muts = np.zeros(ref_lengths[read.reference_name])
    output = np.asarray([np.nan]*ref_lengths[read.reference_name])

    # mark off all positions covered by the read
    pos = range(read.reference_start, read.reference_end)
    output[pos] = 0

    output[mutation_list] = 1

    if quals:
        # remove information from poor quality positions
        output[invalid_pos] = np.nan
    output = output[ref_trim[read.reference_name][0]:ref_trim[read.reference_name][1]]
    
    return output

def parse_md(a):
    '''
    Parse MD string, separating text from numbers 
    12T3^CC0C -> [12,3,0] & ['T','^CC','C']
    @ params:   
        a - MD string from read
    @ output:
        text - list of text portions of MD string
        nums - list of integer portions of MD string
    '''
    a = list(a)
    for i in range(len(a)):
       try: a[i]=int(a[i])
       except ValueError: pass

    text= []
    nums = []
    if isinstance(a[0], int):
       text_mode = False
    else:
       text_mode = True
       nums = [0]

    curr = a[0]
    for i in range(1, len(a)):
       if text_mode:
          if type(a[i-1])==type(a[i]):
             curr += a[i]
          else:
             text.append(curr)
             curr=a[i]
             text_mode = not text_mode
       else:
          if type(a[i-1])==type(a[i]):
             curr = curr*10+a[i]
          else:
             nums.append(curr)
             curr=a[i]
             text_mode = not text_mode
    if isinstance(curr, int):
       nums.append(curr)
    else:
       text.append(curr)
    return text, nums

def get_positions(md, use_deletions = False):
    '''
    Finds the mutations, deletions and their respective positions, 
    zero-indexed from the start of the read
    @ params:   
        md - MD string from read
        use_deletions - Bool: True if deletions are considered as mutations
    @ output:
        muts - list of tuples of (mutation_base, mutations_position)
        dels - list of tuples of (deletion_base, deletion_position)
    '''
    text, nums = parse_md(md)
    muts = []
    dels = []
    pos = 0 
    for i in range(len(text)):
       pos += nums[i]
       if text[i][0]!='^':
          for j in range(len(text[i])):
             muts.append((text[i][j], pos+j))
             pos += 1
       else:
          dl = text[i]
          for d in range(1, len(dl)):
             dels.append((dl[d],pos))
             if use_deletions:
                muts.append((dl[d],pos))
             pos += 1
    return muts, dels

def combine_quals(read, dels, use_deletions = False):
    '''
    Computes the quality scores of each sequenced position
    @ params:   
        read - aligned read segment 
        dels - list of tuples (deletion_base, deletion_position)
        use_deletions - Bool:  True if deletions are considered as mutations
    @ output:
        v_pos - list of quality score relative to the start of the read
    '''
    d_pos = set([i for (j,i) in dels]) # list of positions containing deletions, relative to read start
    if use_deletions:
        del_score = 30
    else:
        del_score = 0
    v_pos = [] # valid positions by quality score
    index = 0
    for i in range(read.reference_end - read.reference_start):
        if i in d_pos: 
            v_pos.append(del_score)
            continue
        v_pos.append(read.query_alignment_qualities[index])
        index += 1
    return np.array(v_pos)



























