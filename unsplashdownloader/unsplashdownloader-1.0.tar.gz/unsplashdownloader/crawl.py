#!/usr/bin/env python3

import urllib.request
import json
import re
import time
import argparse
import os
import sys
import shutil
from tqdm import tqdm
from bs4 import BeautifulSoup
from slimit import ast
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor

def get_args():
    parser = argparse.ArgumentParser(
        description="Scrap a unsplash first 24 pictures userpage")
    parser.add_argument("dst", metavar="destination", nargs="?", default=None,
        help="folder destination")
    parser.add_argument("user", metavar="user", nargs="?", default=None,
        help="username to scrap, or complete URL")
    return parser.parse_args()

def check_args(args):
    if not args.dst or not args.user:
        print("Failed to detect destination or user parameters")
        sys.exit(1)
    if not os.path.exists(args.dst):
        print("Path: " + args.dst + " doest not exists")
        sys.exit(1)
    if not os.path.isdir(args.dst):
        print("Path: " + args.dst + " is not a directory")
        sys.exit(1)
    if not args.user.startswith("https://"):
        args.user = "https://unsplash.com/@" + args.user
    try: 
        urllib.request.urlopen(args.user)
    except Exception as e:
        print("Could not ping unsplash page")
        print(str(e))
        sys.exit(1)
    print("URL: " + args.user)
    print("Destination: " + args.dst)

def get_soup(args):
    r = urllib.request.urlopen(args.user).read()
    return BeautifulSoup(r, 'html.parser')

def get_pic_urls(soup, index):
    data = None
    for script in soup.find_all('script'):
        if '__ASYNC_PROPS__' in str(script):
            script = str(script)
            script = script.replace('<script>__ASYNC_PROPS__ = ', '')
            script = script.replace('</script>', '')
            data = script
            break
    data = json.loads(data)[index]
    pic_ids = []
    for id in data["asyncPropsPhotoFeed"]["photoIds"]:
        pic_ids.append(id)
    pic_url = []
    for id in pic_ids:
        pic_url.append(data["asyncPropsPhotos"][id]["urls"]["raw"])
    return pic_url

def progress_hook(t):
    last_b = [0]
    def inner(b=1, bsize=1, tsize=None):
        if tsize is not None:
            t.total = tsize
            t.update((b - last_b[0]) * bsize)
            last_b[0] = b
    return inner

def download_pics(pic_url, args):
    print("Found " + str(len(pic_url)) + " pictures")
    col, line = shutil.get_terminal_size()
    print(" Downloads ".center(col, "="))
    for url in pic_url:
        t = tqdm(unit='B', unit_scale=True, miniters=1)
        t.set_description(url.rsplit('/', 1)[-1])
        urllib.request.urlretrieve(url, args.dst + url.rsplit('/', 1)[-1]
                + ".png", progress_hook(t))
        t.close()
        time.sleep(0.3)
    print(" Downloads Done ".center(col, "="))

def main():
    args = get_args()
    check_args(args)
    soup = get_soup(args)
    pic_url = get_pic_urls(soup, 1 if "@" in args.user else 0)
    download_pics(pic_url, args)
