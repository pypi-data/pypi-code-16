#!/usr/bin/env python

"""Usage: kaptl init <name> (<rules> | --rules-file=RULESFILE) --license=KEY [--build] [--recipe=RECIPENAME] [--backend=STACK] [--frontend=STACK] [--recipe-version=VERSION] [--skip-ssl-check] [--kaptl-url=KAPTLURL]
       kaptl update [--build] [--license=KEY] [--recipe=RECIPENAME] [--mode=full|partial] [--recipe-version=VERSION] [--skip-ssl-check] [--kaptl-url=KAPTLURL]
       kaptl add <rule> [--build] [--license=KEY] [--recipe=RECIPENAME]
       kaptl parse (<rules> | --rules-file=RULESFILE) [--license=KEY] [--recipe=RECIPENAME] [--recipe-version=VERSION] [--skip-ssl-check] [--kaptl-url=KAPTLURL]
       kaptl project schema (<rules> | --rules-file=RULESFILE) [--license=KEY] [--recipe=RECIPENAME] [--recipe-version=VERSION] [--output=OUTPUT] [--skip-ssl-check] [--kaptl-url=KAPTLURL]
       kaptl recipe versions [--license=KEY] [--recipe=RECIPENAME] [--skip-ssl-check] [--kaptl-url=KAPTLURL]
       kaptl show
       kaptl status
       kaptl -h | --help

Commands:
    init                    Initialize a new application in a current directory
    update                  Regenerate an existing application.
                            Requires .kaptl directory to be present in the directory.
    recipe versions         Returns all available versions for recipe
    project schema          Returns project schema json
    show                    Get information about current project
    status                  See if the rules have been changed but update wasn't performed
    add                     Add rule string to a rules file for current project

Arguments:
    <name>                  Inline app name.
    <rules>                 Inline string with KAPTL rules.
                            See --rules-file  to use a text file instead

Options:
    -b STACKNAME --backend=STACKNAME           Backend framework. Possible values are: "mvc", "sails".
                                               If not specified, backend won't be generated
    -f STACKNAME --frontend=STACKAME           Frontend framework. Possible values are: "angular".
                                               If not specified, frontend won't be generated
    -r RULESFILE --rules-file=RULESFILE        Path to a file with KAPTL Rules
    -i --build                                 Build the project after it is unpacked
    --recipe=RECIPENAME                        Recipe to use when generating the application.
                                               Possible values are "cms", "stripe", "master".
                                               If not specified, "master" will be used as a default value.
    --recipe-version=VERSION                   Recipe version used to generated application.
                                               If not specified, manifest version will be used.
                                               If manifest file does not exists, latest version will be used.
    -h --help                                  Open this window
    -l --license=KEY                           Specify the license key to use for this request
    --mode=full|partial                        Full option updates the local boilerplate with server version.
                                               This can result in major breaking changes but may be necessary
                                               when updating local build to a new version of the recipe.
                                               Default is "partial"
    --skip-ssl-check                           Disable SSL Certificate check on API calls.
    --kaptl-url=KAPTLURL                       Url to kaptl server. https://www.kaptl.com by default
  

"""
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from KaptlInit import *
from KaptlShow import KaptlShow
from KaptlUpdate import KaptlUpdate
from docopt import docopt
from KaptlStatus import *
from KaptlAdd import KaptlAdd
from KaptlParse import KaptlParse
from KaptlProject import KaptlProject
from KaptlVersions import KaptlVersions
from Utils import Utils

def checkLicense():
    args = docopt(__doc__)
    al = args["--license"]

    if al:
        Utils.set_manifest_data("license",al)
        return al
    ml = Utils.manifest("license")

    if ml:
        return ml

    print "Use of KAPTL requires a license key. Obtain a valid key at www.kaptl.com and use --license" \
    " to provide your key to the CLI."
    sys.exit()

def main():
    args = docopt(__doc__)
    session = requests.Session()

    print "KAPTL CLI (c) 8th Sphere, Inc."

    #Parse parameters and launch the proper operation
    #:type arguments: object

    rec = args["--recipe"]
    if rec:
        Utils.set_manifest_data("recipe",rec)

    if args["init"]:
        checkLicense()
        if os.path.exists(os.getcwd() + "/.kaptl"):
            print "There is an existing project in a current directory. Aborting..."
            sys.exit()
        else:
            init = KaptlInit(session, args)
            init.initialize_project()
            Common.display_app_info()

    if args["status"]:
        status = KaptlStatus()
        status.display()

    if args["update"]:
        checkLicense()
        update = KaptlUpdate(session, args)
        update.update_project()
        Common.display_app_info()

    if args["show"]:
        show = KaptlShow()
        show.output_project_info()

    if args["add"]:
        checkLicense()
        add = KaptlAdd(args)
        add.add_rule_to_rules_file()
        update = KaptlUpdate(session, args)
        update.update_project()

    if args["--build"]:
        Utils.build_project()

    if args["parse"]:
        checkLicense()
        init = KaptlParse(session, args)
        init.parse()

    if args["project"] and args["schema"]:
        checkLicense()
        init = KaptlProject(session, args)
        init.project()

    if args["recipe"] and args["versions"]:
        checkLicense()
        init = KaptlVersions(session, args)
        init.versions()

        #Common.parse_rules(session,args["<rules>"],Utils.get_stack_info(args),None,l,args["--recipe"])

if __name__ == '__main__':
    "Main entry point for KAPTL CLI"
    main()
