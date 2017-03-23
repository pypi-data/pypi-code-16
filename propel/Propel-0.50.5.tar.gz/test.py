import argparse

__title__ = "Propel"
__version__ = "0.50.0"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="%s %s" % (__title__, __version__))
    parser.add_argument("-w", "--webs", help="Deploy sites by name ", nargs='*')
    parser.add_argument("--all-webs", help="Deploy all sites", action="store_true")
    parser.add_argument("-s", "--scripts",
                        help="Run script by specifying name:"
                             " ie: [-s pre_web post_web other_one]",
                        nargs='*')
    parser.add_argument("-k", "--workers",
                        help="Run Workers by specifying name: ie [-k tasks othertasks]",
                        nargs='*')
    parser.add_argument("-r", "--reload", help="To refresh the servers",
                        action="store_true")
    parser.add_argument("-x", "--undeploy", help="To UNDEPLOY the application",
                        action="store_true")
    parser.add_argument("-m", "--maintenance",
                        help="Values: on|off - To set the site on maintenance. ie [--maintenance on]")
    parser.add_argument("-c", "--create",
                        help="Create a new application repository, set the git init for web push")
    parser.add_argument("--basedir",
                        help="The base directory when creating a new application. By default it's /home")
    parser.add_argument("--silent", help="Disable verbosity",
                        action="store_true")
    parser.add_argument("--ps", help="Show all the Supervisor processes",
                        action="store_true")
    parser.add_argument("--restart",
                        help="Restart all managed Supervisor processes",
                        action="store_true")

    parser.add_argument("--git-init",
                        help="Setup a git bare repo $name to push content to. [--git-init $name]")
    parser.add_argument("--git-push-web",
                        help="Set propel to deploy automatically when "
                             "push to the bare repo. [--git-push-web $name]")
    parser.add_argument("--git-push-cmd",
                        help="Setup Command to execute after git push. Put cmds within quotes"
                             "ie: [--git-push-cmd $name 'ls  -l' 'cd ']",
                        nargs='*')
    parser.add_argument("--debug", help="To output the full error stack in",
                        action="store_true")
    arg = parser.parse_args()
    VERBOSE = False if arg.silent else True

    print(arg.webs)
    print(arg.all_webs)
