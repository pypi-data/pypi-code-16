import os
import sys
import uuid
from Utils import Utils
from Common import Common
from exceptions import *
import os
import sys
import zipfile

import pyprind
import requests

class KaptlClient:
    # KAPTL_HOST = "http://kaptl.dev"
    DEFAULT_KAPTL_URL = "https://www.kaptl.com"
    # KAPTL_HOST = "https://dev.kaptl.com"
    # KAPTL_HOST = "http://localhost:62958"

    def __init__(self, session, args):
        self.arguments = args
        self.session = session
        self.license = self.arguments["--license"]
        self.verify_request = not self.arguments["--skip-ssl-check"]
        self.kaptl_url = self.DEFAULT_KAPTL_URL
        if self.arguments["--kaptl-url"]:
            self.kaptl_url = self.arguments["--kaptl-url"]
        self.kaptl_parse_url = self.kaptl_url + "/api/apps/parse"
        self.kaptl_download_url = self.kaptl_url + "/api/apps/download"
        self.kaptl_project_url = self.kaptl_url + "/api/apps/project-schema"
        self.kaptl_versions_url = self.kaptl_url + "/api/apps/recipe-version"


    def parse_rules(self, rules, stack, recipe=None, app_name = "", recipe_version=""):
        print "Parsing the rules..."
        try:
            response = self.send_parse_rules_request(rules, stack, recipe, recipe_version, app_name)
            if response.status_code != 200:
                print "ERROR: API is unavailable at the moment, please try again later. Status Code = " + str(
                    response.status_code)
                sys.exit()

            response_content = response.json()
            if response.status_code and response_content["success"]:
                print "KAPTL build completed successfully."
                return response_content["sessionName"]
            else:
                print "ERROR: KAPTL build error."
                if response_content["compilerOutput"]:
                    print response_content["compilerOutput"]
                return None
        except requests.exceptions.RequestException as e:
            print "ERROR: API is unavailable at the moment, please try again later", e
            sys.exit()
        except ValueError as ex:
            print "ERROR: cannot process request JSON", ex.message
            sys.exit()

    def send_parse_rules_request(self, rules, stack, recipe=None, recipe_version="", app_name="", return_compiler_output = False):
        request_data = dict(
            rulesText=rules.replace('\\', '').replace('\'', '"'),
            stack=stack,
            licenseKey=self.license,
            recipe=recipe,
            appName=app_name,
            returnCompilerOutput=return_compiler_output,
            recipeVersion=recipe_version)

        kaptl_cookie = {"kaptl-session-id": app_name}
        if recipe is not None:
            request_data["recipe"] = recipe
        try:
            if kaptl_cookie is not None:
                response = self.session.post(self.kaptl_parse_url, json=request_data, cookies=kaptl_cookie, verify=self.verify_request)
            else:
                response = self.session.post(self.kaptl_parse_url, json=request_data, verify=self.verify_request)
            return response
        except requests.exceptions.RequestException as e:
            print "ERROR: API is unavailable at the moment, please try again later", e.message
            sys.exit()
            
    def send_project_request(self, rules, stack, recipe=None, app_name="", recipe_version=""):
        request_data = dict(
            rulesText=rules.replace('\\', '').replace('\'', '"'),
            stack=stack,
            licenseKey=self.license,
            recipe=recipe,
            appName=app_name,
            returnCompilerOutput=False,
            recipeVersion=recipe_version)
        try:
            response = self.session.post(self.kaptl_project_url, json=request_data, verify=self.verify_request)
            return response
        except requests.exceptions.RequestException as e:
            print "ERROR: API is unavailable at the moment, please try again later", e.message
            sys.exit()

    def send_versions_request(self, recipe):
        request_data = dict(
            licenseKey=self.license,
            recipe=recipe)
        try:
            response = self.session.post(self.kaptl_versions_url + "/" + recipe, json = request_data, verify=self.verify_request)
            return response
        except requests.exceptions.RequestException as e:
            print "ERROR: API is unavailable at the moment, please try again later", e.message
            sys.exit()

    
    def get_versions(self, recipe):
        response = self.send_versions_request(recipe)
        response_content = response.json()
        return response_content["recipeVersions"]

    def isUpdate(self, mode):
        if mode is None:
            return True
        if mode == "full":
            return False
        return True

    def get_file_info(self, session_name, rules, stack, recipe, mode, angular_only=False, app_id=0, app_name=None, email=None):
        print "Downloading the generated app..."
        request_data = dict(app = {
            'appId': app_id,
            'sessionName': session_name,
            'appName': app_name,
            'rulesText': rules,
            'stack': stack,
            'licenseKey': self.license,
            'recipe': recipe
        }, email=email, angularOnly=angular_only, isUpdate=self.isUpdate(mode))

        try:
            response = self.session.post(self.kaptl_download_url, json=request_data, verify=self.verify_request)
            response_content = response.json()
            if response.status_code and response_content["success"]:
                return response_content["fileUrl"], response_content["fileName"]
            else:
                return None
        except requests.exceptions.RequestException as e:
            print "ERROR: API is unavailable at the moment, please try again later.", e.message
            sys.exit()

    def download_file(self, file_info):
        try:
            with open(file_info[1], 'wb') as f:
                r = self.session.get(file_info[0], stream=True)
                total_length = int(r.headers.get('content-length'))
                bar = pyprind.ProgBar(total_length / 1024)
                if total_length is None:  # no content length header
                    f.write(r.content)
                else:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                        bar.update()
        except IOError as e:
            print "ERROR: Couldn't download a file", e.message
            sys.exit()