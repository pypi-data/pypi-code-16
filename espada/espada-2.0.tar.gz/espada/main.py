
import click
import os
import inflection
import datetime
from jinja2 import Environment, PackageLoader, select_autoescape
import urllib

today = datetime.date.today()

env = Environment(
    loader=PackageLoader('espada', 'templates'),
    autoescape=select_autoescape(['cpp', 'h', 'txt'])
)


@click.group()
def cli():
    #print(os.getcwd())
    pass


@cli.command()
@click.argument('project_name') # , help="Name of Project"
def project(project_name):
    """Generate a C++ Project"""
    print('Generating project')
    generate_project_folder(project_name)


@cli.command('class')
@click.option('--class', '-c', 'class_name', prompt='Name of the class',
              help="Name of Class to generate ")
@click.option('--test', is_flag=True, help="Generate test case for class")
def class_gen(class_name, test):
    """Generate C++ Class file with given name"""
    if os.path.isdir("lib"):
        generate_class_header(class_name)
        generate_class_body(class_name)
        if(test):
            generate_class_test(class_name)
    else:
        print "Please make sure you are in the main project directory"


@cli.command('test')
@click.option('--class', '-c', 'class_name', prompt='Name of the class to test',
              help="Name of Class to generate a test case for")
def test_gen(class_name):
    """Generate Unit test based on given class name"""
    if os.path.isdir("tests"):
        generate_class_test(class_name)
    else:
        print "Please make sure you are in the main project directory"


@cli.command('header')
@click.option('--proj', '-p', 'project', type=click.Choice(['lib', 'app']), prompt="Project to Create Header")
@click.option('--file', '-f', 'name', prompt='Name of the file', help="Name of header file to create")
def header_gen(project, name):
    """Generate a empty Header File"""
    if os.path.isdir(project):
        if os.path.isdir("{0}/include".format(project)):
            generate_empty_file(name, project, "h", "include")
        else:
            os.mkdir("{0}/include".format(project))
            generate_empty_file(name, project, "h", "include")
            print "Please remember to remove the # sign from the include_directories command at " \
                "the top of the CMakeLists file in the {0} directory".format(project)
    else:
        print "Please make sure you are in the main project directory"


@cli.command('source')
@click.option('--proj', '-p', 'project', type=click.Choice(['lib', 'app']), prompt="Project to create source")
@click.option('--file', '-f', 'name', prompt='Name of the file', help="Name of source file to create")
def source_gen(project, name):
    """Generate a empty source File"""
    if os.path.isdir(project):
        generate_empty_file(name, project, "cpp", "src")
    else:
        print "Please make sure you are in the main project directory"


def generate_project_folder(name):
    proj_name = inflection.camelize(name)
    os.mkdir(proj_name)
    os.chdir(proj_name)
    args = {
        'project_name': proj_name,
        'exe_name': inflection.underscore(proj_name)
    }
    generate_file_from_template('project_cmake.txt', 'CMakeLists.txt', **args)
    generate_lib_project(**args)
    generate_test_project(**args)
    generate_main_project(**args)


def generate_lib_project(**kwargs):
    os.mkdir('lib')
    os.chdir('lib')
    generate_file_from_template('lib_cmake.txt', 'CMakeLists.txt', **kwargs)
    os.mkdir('include')
    generate_file_from_template('gitkeep.txt', 'include/.gitkeep', **kwargs)
    os.mkdir('src')
    generate_file_from_template('gitkeep.txt', 'src/.gitkeep', **kwargs)
    os.chdir('..')


def generate_test_project(**kwargs):
    os.mkdir('tests')
    os.chdir('tests')
    generate_file_from_template('tests_cmake.txt', 'CMakeLists.txt', **kwargs)
    os.mkdir('include')
    testfile = urllib.URLopener()
    testfile.retrieve("https://raw.githubusercontent.com/philsquared/Catch/master/single_include/catch.hpp",
                      "include/catch.hpp")
    testfile.retrieve("https://raw.githubusercontent.com/eranpeer/FakeIt/master/single_header/catch/fakeit.hpp",
                      "include/fakeit.hpp")
    os.mkdir('src')
    generate_file_from_template('test_main.cpp', 'src/main.cpp', **kwargs)
    os.chdir('..')


def generate_main_project(**kwargs):
    os.mkdir('app')
    os.chdir('app')
    generate_file_from_template('app_cmake.txt', 'CMakeLists.txt', **kwargs)
    os.mkdir('src')
    generate_file_from_template('app_main.cpp', 'src/main.cpp', **kwargs)
    os.chdir('..')


def generate_class_header(name):
    args = generate_args(name)
    generate_file_from_template('class_header.h', "lib/include/{0}.h".format(args['f_name']), **args)


def generate_class_body(name):
    args = generate_args(name)
    generate_file_from_template('class_body.cpp', "lib/src/{0}.cpp".format(args['f_name']), **args)


def generate_class_test(name):
    args = generate_args(name)
    generate_file_from_template('test_case.cpp', "tests/src/{0}_tests.cpp".format(args['f_name']), **args)


def generate_args(name, ext='cpp'):
    return {
        'class_name': inflection.camelize(name),
        'f_name': inflection.underscore(name),
        'user_name': os.environ.get('USER', ''),
        'ext': ext,
        'date_time': "{:%d, %b %Y }".format(today)
    }


def generate_empty_file(name, proj, ext, dest):
    args = generate_args(name, ext)
    generate_file_from_template('empty_src.cpp', "{0}/{1}/{2}.{3}".format(proj, dest, args['f_name'], ext), **args)


def generate_file_from_template(template_name, file_name, **kwargs):
    template = env.get_template(template_name)
    target = open(file_name, 'w')
    target.write(template.render(**kwargs))
    print "Generated {0}".format(file_name)

