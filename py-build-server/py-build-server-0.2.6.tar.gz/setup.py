import os
import sys
from setuptools import setup, find_packages

if sys.version > (3, ):
    sys.exit('Sorry, Python3 is not supported at this stage.')
if not os.path.isdir('/etc/py-build-server'):
    os.mkdir('/etc/py-build-server')
if not os.path.isfile('/etc/py-build-server/config.yaml'):
    default_config = """# Demo entry using all possible config options: O denotes optionals
####
#
### this section defines how to check for changes
#
# repository_update_method: polling  # (O) poll git repo
# repository_update_method:          # (O) --alternatively--
#     webhook:                       # (O) specify webhook to recieve notifications from github
#         subdomain: /               # (O) listen to this subdomain (http://<your_url/)
#         listen_address: 0.0.0.0    # (O) listen on this local address (0.0.0.0 listens to all)
#
### this section set logging options
#
# logging:                           # (O)
#     level: debug                   # (O) DEBUG|WARN|INFO|ERROR|OFF (case doesnt matter)
#     implement_journald: false      # (O) send logs to journald instead
#
### this section sets repository specific settings
# repositories:
#     repo_one:  # needs to match github if using webhooks
#         dir: /path/to/repository/root
#         interval: 10               # (O) minutes between repo checks (only needed if polling)
#         remote: origin             # (O) remote name to fetch (default: origin)
#         branch: branch_to_release  # (O) if set, dont upload unless on this branch
#         twine_conf:                # this whole section of options are optional, but you will need
#                                    # to supply user/pass or pypirc file
#             username: user         # (O) username to authenticate to repository as
#             password: pass         # (O) password to authenticate to repository with
#             repository:            # (O) repo to upload to (default: pypi)
#             gpg_sign: true|false   # (O) sign files to upload using gpg
#             gpg_program:           # (O) program used to sign uploads(default: gpg)
#             gpg_identity:          # (O) gpg identity used to sign files
#             comment:               # (O) comment to include with distribution file
#             pypirc_file:           # (O) the .pypirc file to use
#             skip_existing: false   # (O) continue uploading if one already exists
    \n"""
    with open('/etc/py-build-server/config.yaml', 'w+') as config_file:
        config_file.write(default_config)
        wrote_config = True
setup(
    name='py-build-server',
    version='0.2.6',
    packages=find_packages(),
    license='GPL3',
    author='chestm007',
    url='https://github.com/chestm007/py_build_server',
    author_email='chestm007@hotmail.com',
    description='My build server i run on my home server to check for git repo tags, and push to pypi',
    entry_points="""
        [console_scripts]
        py-build-server=py_build_server.main:cli
    """,
    requires=[
        'click',
        'gitpython',
        'pyyaml'
    ]
)

if wrote_config:
    print('you will need to modify the config file located in /etc/py-build-server\n'
          'and change the file ownership to the daemon user that will run this process\n')