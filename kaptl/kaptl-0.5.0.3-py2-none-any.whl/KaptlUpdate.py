import os
import sys

from KaptlClient import KaptlClient
from Utils import Utils

from Common import Common


class KaptlUpdate:
    def __init__(self, session, arguments):
        try:
            for filename in os.listdir(os.getcwd() + "/.kaptl"):
                if filename.endswith(".kaptl.old"):
                    self.app_name = Utils.get_manifest_data()["appName"]
        except WindowsError:
            print("There was an error with Kaptl Update, it seems your .kaptl folder may be missing.")
            sys.exit(3)

        if self.app_name is "":
            print "ERROR: Directory does not contain a KAPTL project"
            sys.exit()

        rec = arguments["--recipe"]
        if rec:
            try:
                oldRecipe = Utils.get_manifest_data()["recipe"]
                if oldRecipe != rec:
                    # Change in the recipe continue to update the recipe
                    print("Changing recipe from {} to {}\n".format(oldRecipe, rec))
                    Utils.set_manifest_data("recipe", rec)
            except KeyError:
                print("Old recipe not found in manifest, setting recipe to {}.".format(rec))
                Utils.set_manifest_data("recipe",rec)



        self.arguments = arguments
        self.session = session
        arguments["--license"] = Utils.manifest("license") if not arguments["--license"] else arguments["--license"]
        self.kaptl_client = KaptlClient(session, arguments)

        self.current_recipe_version = Utils.get_manifest_data().get("recipeVersion", None)
        self.recipe_version = "" if not self.arguments["--recipe-version"] else self.arguments["--recipe-version"]
        self.recipe = Utils.manifest("recipe")
        if not self.recipe:
            print("ERROR: Recipe not found in manifest or not set in command parameters.")
            sys.exit()

        self.rules = Utils.read_rules_from_file(os.getcwd() + "/app.kaptl")
        self.rules_old = Utils.read_rules_from_file(os.getcwd() + "/.kaptl/app.kaptl.old")
        self.file_info = None
        self.angular_only = False
        self.stack = Utils.get_stack_info_from_manifest()
        self.app_id = Utils.get_id_from_manifest()
        self.angular_only = Utils.check_if_angular_only(self.stack)
        self.mode = arguments["--mode"]
        self.verify_requests = not self.arguments["--skip-ssl-check"]



    def get_version_to_update(self):
        if self.recipe_version != "":
            print "Update to recipe version: " + self.recipe_version
            return self.recipe_version
        ##version not set, so check current version compatibility##
        available_versions = self.kaptl_client.get_versions(recipe=self.recipe)
        for version in available_versions:
            if version == self.current_recipe_version:
                print "Update to current recipe version: " + version
                return version
        print "Update to latest recipe version"
        return ""



    def update_project(self):
        version_to_update = self.get_version_to_update()
        session_name = self.kaptl_client.parse_rules(self.rules, stack=self.stack, recipe=self.recipe, app_name=self.app_name, recipe_version=version_to_update)
        if session_name is not None:
            self.file_info = self.kaptl_client.get_file_info(session_name, self.rules, self.stack,
                                                               self.recipe, self.mode, self.angular_only, self.app_id,
                                                                self.app_name)
            if self.file_info is not None:
                self.kaptl_client.download_file(self.file_info)
                Common.unzip_archive(self.file_info[1], existing=False)
            else:
                print "ERROR: Couldn't retrieve a file from the server. Try again later."
                sys.exit()
        else:
            # just exit, parse_rules will print the info about what happened
            sys.exit()
