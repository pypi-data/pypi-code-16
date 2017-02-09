"""Script for generating python project."""
import os
import argparse
from src.project_config import ProjectConfiguration
from src.project_generator import ProjectGenerator
from src.metadata import VERSION
from scripts.generate_template import generate_json, generate_yaml


def main():
    """Python project generation main function."""
    parser = get_argparser()
    arguments = parser.parse_args()
    if arguments.template:
        if arguments.template == "json":
            generate_json()
        else:
            generate_yaml()
    elif arguments.file:
        conf_path = arguments.file
        root_path = get_root_path(arguments)
        generate_project(conf_path, root_path)
    else:
        print("Usage error: Either config file or template type must be given.")
        print("Run 'generate-project -h' for help.")


def get_argparser():
    """Initializes the command line argument parser."""
    description = "Generate structure for python project."
    parser = argparse.ArgumentParser(prog='generate-project', description=description)
    parser.add_argument('--version', action='version', version='%(prog)s '+VERSION)
    parser.add_argument('-f', '--file', dest='file', action='store')
    parser.add_argument('-t', dest='template', action='store', choices=['yaml', 'json'])
    parser.add_argument('-o', '--output', dest='output', action='store')
    return parser

def get_root_path(cmd_parser):
    """Get root path fro project generation."""
    if cmd_parser.output:
        root_path = cmd_parser.output
    else:
        root_path = os.getcwd()
    return root_path


def generate_project(conf_file, root_path):
    """Generates the project stub."""
    config = ProjectConfiguration(conf_file)
    generator = ProjectGenerator(config)
    generator.generate(root_path)


if __name__ == '__main__':
    main()
