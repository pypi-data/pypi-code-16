#!/usr/bin/python
# -*- coding: UTF-8 -*-

movies = ["The Holy Grail",1975,"Terry Gilliam",91,
           ["Graham Chapman",
            ["Michael Palin","John Cleese","Terry Gilliam","Eric Idle","Terry Jones"]]]

def print_lol(the_list,level):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                print ("\t")
            print(each_item)




