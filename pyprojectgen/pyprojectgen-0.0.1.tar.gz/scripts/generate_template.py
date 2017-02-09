"""Script for generating project template file."""
import sys
from src.template_builder import TemplateBuilder


def main():
    """Main function of the template generator script."""
    if "-j" in sys.argv:
        generate_json()
    else:
        generate_yaml()

def generate_json():
    """Generates template in json."""
    with open("config_project.json", "w") as stream:
        content = TemplateBuilder.build_json()
        stream.write(content)


def generate_yaml():
    """Generates template in yaml."""
    with open("config_project.yml", "w") as stream:
        content = TemplateBuilder.build_yaml()
        stream.write(content)


if __name__ == '__main__':
    main()
