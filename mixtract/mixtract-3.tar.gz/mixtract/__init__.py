import os
import sys
import yaml

from . import cli

# Basic settings
API_VERSION = '2.0'
config_path = os.path.join(os.getcwd(), 'mixtract.yaml')

# Check whether the config file exists.
try:
    with open(config_path, 'r') as f:
        config = yaml.load(f)
except:
    print(("Error: the configuration file is absent. Create mixtract.yaml "
           "in the current folder."))
    sys.exit(1)

def main():
    cli.execute()

if __name__ == '__main__':
    main()
