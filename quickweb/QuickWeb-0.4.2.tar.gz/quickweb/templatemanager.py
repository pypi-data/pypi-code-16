# !/usr/bin/python
from __future__ import print_function

try:
    from html.parser import HTMLParser
except  ImportError:
    from HTMLParser import HTMLParser   # Python2 compatibility

from os.path import basename, join, exists, dirname
from quickweb._tempfile import TemporaryDirectory
import os
import sys
import shutil
import io
import requests
import zipfile


TEMPLATES_REPO = 'https://github.com/MyWayOS/QuickWeb-templates/archive/master.zip'

class MyHTMLParser(HTMLParser):
    def __init__(self, url, template_directory):
        HTMLParser.__init__(self)
        self.template_directory = template_directory
        self.url = url
        self.replacement_map = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link':
            self.fetch_static_asset(attrs['href'])
        if tag == 'script' and 'src' in attrs:
            self.fetch_static_asset(attrs['src'])

            # print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        return
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        data = data.strip(' \r\n')
        if data:
            print("Encountered some data  :", data)

    def fetch_static_asset(self, url):
        print(self.template_directory, url)
        if url.split(':')[0] in ['http', 'https']:  # External resource
            print("WARNING: External resource", url, 'Skipping')
            return
        fetch_url = self.url + url
        output_filename = basename(fetch_url)
        resource_extension = url.split('.')[-1]
        resource_map = {
            'js': join('static', 'js'),
            'css': join('static', 'css'),
            'ico': None,
        }
        resource_type = resource_map.get(resource_extension, None)
        if resource_type is None:
            print("WARNING: Ignoring resource", url)
            return
        output_dir = join(self.template_directory, resource_map[resource_extension])
        if output_dir is None:  # We don't fetch icons
            return
        print("Fetching %s ->  %s/%s" % (fetch_url, output_dir, output_filename))
        os.makedirs(output_dir, mode=0o755, exist_ok=True)
        resource = requests.get(fetch_url)

        with open(join(output_dir, output_filename), 'w') as static_file:
            static_file.write(resource.text)
        self.replacement_map[url] = '/'+join(resource_extension, output_filename)


class TemplateMaker:
    def __init__(self, url, template_directory):
        self.url = url
        if template_directory is None:
            template_directory = url.strip('/').split('/')[-1]
        self.template_directory = template_directory

    def make(self, force):
        if exists(self.template_directory):
            if force:
                shutil.rmtree(self.template_directory)
            else:
                sys.stderr.write(self.template_directory + ' already exists!\n\
                Please use --force if you want to overwrite.\n')
                sys.exit(2)

        # Fetch the page
        page = requests.get(self.url)
        parser = MyHTMLParser(self.url, self.template_directory)
        html = page.text

        # Fetch any static elements
        parser.feed(page.text)

        # Replace resource urls with our uniformed static locations
        for old, new in parser.replacement_map.items():
            print(old, new)
            html = html.replace(old, new)

        # Create the index.html
        webroot_dir = join(self.template_directory, 'webroot')
        os.makedirs(webroot_dir, mode=0o755, exist_ok=force)
        index_filename = join(webroot_dir, 'index.html')
        print("Creating ", index_filename)
        with open(index_filename, 'w') as index_file:
            index_file.write(html)

        print("\nMake completed.")
        print("You can now execute:\n\t quickweb run", self.template_directory)

class Downloader:
    def __init__(self, template_name, app_directory):
        self.template_name = template_name
        self.app_directory = app_directory

    def download(self, force):
        if exists(self.app_directory):
            if force:
                shutil.rmtree(self.app_directory)
            else:
                sys.stderr.write(self.app_directory + ' already exists!\n\
                Please use --force if you want to overwrite.\n')
                sys.exit(2)
        page = requests.get(TEMPLATES_REPO)
        file_like_object = io.BytesIO(page.content)
        templates_archive = zipfile.ZipFile(file_like_object)
        with TemporaryDirectory() as tmpdirname:
            templates_archive.extractall(tmpdirname)
            templates_archive_tmp = join(tmpdirname, 'QuickWeb-templates-master')
            template_dirs = os.listdir(templates_archive_tmp)
            if self.template_name not in template_dirs:
                sys.stderr.write('Unable to find templae %s .\n' % self.template_name)
                sys.exit(2)
            template_root = join(templates_archive_tmp, self.template_name)
            print("%s -> %s" % (template_root, self.app_directory))
            shutil.copytree(template_root, self.app_directory)
            print("Init completed.")
