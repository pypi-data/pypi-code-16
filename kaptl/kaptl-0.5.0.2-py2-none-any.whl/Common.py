import os
import sys
import zipfile

import pyprind
import requests


from Utils import Utils

class Common:
    def __init__(self, session):
        self.session = session

    @staticmethod
    def unzip_archive(filename, existing, delete_archive_after_extract=True):
        if existing:
            result = Utils.query_yes_no("This action may override changes you already made to your project "
                                        "in the current directory. Do you want to proceed?")
            if result == "yes" or result == "y":
                Common.extract_achive(filename)
            elif result == "no" or result == "n":
                print "Exiting the program..."
        else:
            Common.extract_achive(filename)


    @staticmethod
    def extract_achive(filename, delete_archive_after_extract=True):
        try:
            with open(filename, "rb") as f:
                z = zipfile.ZipFile(f)
                spec = Utils.get_kaptl_ignore_spec()
                for name in z.namelist():
                    if spec is not None and (name == '.kaptlignore' or spec.match_file(name)):
                        print "ignored", name
                        continue
                    z.extract(name, os.getcwd())

        except IOError as e:
            print "ERROR: Couldn't unzip the file", e.message

        if delete_archive_after_extract:
            try:
                print "Cleaning up..."
                os.remove(filename)
            except IOError as e:
                print "ERROR: Couldn't delete a zip file", e.message


    @staticmethod
    def display_app_info():
        manifest_data = Utils.get_manifest_data()
        recipeVersion = manifest_data["recipeVersion"]
        kaptlVersion = manifest_data["kaptlVersion"]
        appName = manifest_data["appName"]
        print ("Recipe Version: {1}\n"
               "KAPTL Generator Version: {2}").format(appName, recipeVersion, kaptlVersion)
