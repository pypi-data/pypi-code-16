#!/usr/bin/python
# ----------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved. 
#  Licensed under the MIT License. See License.txt in the 
#  project root for license information.  If License.txt is 
#  missing, see https://opensource.org/licenses/MIT
# ----------------------------------------------------------

"""Microsoft Genomics Command-line Client - allows submission and management
 of genomics workflows on the Microsoft Genomics platform"""

#
# Version must be valid form for StrictVersion <d>.<d>.<d> for the sort
# to work properly and find the latest version.  More details at:
# http://epydoc.sourceforge.net/stdlib/distutils.version.StrictVersion-class.html
version = '0.6.15'

import msgen_cli.malibuworkflow as malibuworkflow
import msgen_cli.malibuargs as malibuargs
import sys

def warn_for_package_update():
    """Check for updated version of msgen and warn if a newer version is available"""

    try:
        import requests
        from distutils.version import StrictVersion

        # 'msgen' is our package name.  Construct the URL
        #  to get the msgen package information from pypi
        url = "https://pypi.python.org/pypi/%s/json" % "msgen"
        versions = requests.get(url).json()["releases"].keys()
        versions.sort(key=StrictVersion, reverse=True)
        if version < versions[0]:
            print ("\nThere is a newer version of msgen available."
                   "  Please consider upgrading to v%s."
                   "\nTo upgrade, run: pip install --upgrade msgen\n"
                  ) % versions[0]

    except:
        print "\nException during test for msgen update. Continuing\n"

    return


def main():
    """Main execution flow"""

    # Display logon banner
    print "Microsoft Genomics Command-line Client v%s" % version
    print "Copyright (c) 2017 Microsoft. All rights reserved."

    warn_for_package_update()

    args_output = malibuargs.ArgsOutput()
    args_output.parse_args_from_command_line()
    arg_error = args_output.validate()
    if arg_error:
        print "Error: " + arg_error
        sys.exit(1000)

    workflow_executor = malibuworkflow.WorkflowExecutor(args_output)

    if args_output.command == "SUBMIT":
        # Post new Workflow
        workflow_executor.post_workflow()
    elif args_output.command == "GETSTATUS":
        # Get workflow status
        workflow_executor.get_workflow_status()
    elif args_output.command == "CANCEL":
        # Cancel workflow
        workflow_executor.cancel_workflow()
    elif args_output.command == "LIST":
        # List workflows
        workflow_executor.list_workflows()
    else:
        print "Error: Unknown value of -command. Please use one of SUBMIT, GETSTATUS, CANCEL, LIST"
        sys.exit(1000)

    sys.exit(workflow_executor.current_exit_status)


if __name__ == "__main__":
    main()
