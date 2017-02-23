# -*- coding: utf-8 -*-

"""ant2mvn.

Usage: command_line.py <libs>
  --project.groupId=<project.groupId>
  --project.artifactId=<project.artifactId>
  --project.version=<project.artifactId>
  --local.dependencies.default.groupId=<local.dependencies.default.groupId>
  --local.dependencies.default.version=<local.dependencies.default.version>
  [--local.dependencies.dest=<local.dependencies.dest>]
  [--repo.name=<repo.name>]
  [--repo.host=<repo.host>]
  [--repo.port=<repo.port>]
  [--properties.project.packaging=<packaging>]
  [--properties.project.build.finalName=<finalName>]
  [--properties.project.build.directory=<directory>]
  [--properties.project.build.sourceDirectory=<sourceDirectory>]
  [--properties.project.build.scriptSourceDirectory=<scriptSourceDirectory>]
  [--properties.project.build.testSourceDirectory=<testSourceDirectory>]
  [--properties.project.build.outputDirectory=<outputDirectory>]
  [--properties.project.build.testOutputDirectory=<testOutputDirectory>]
  [--properties.project.build.sourceEncoding=<sourceEncoding>]
  [--resources.default=<resources.default>]
  [--resources.test=<resources.test>]

  command_line.py -h | --help
  command_line.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --repo.name=<repo.name>    Repository for searching [default: maven_central_repo].
  --repo.host=<repo.host>    Repository host [default: search.maven.org].
  --repo.port=<repo.port>    Repository port [default: 80].
  --local.dependencies.dest=<local.dependencies.dest>                       Local dependencies destication directory [default: lib].
  --properties.project.packaging=<packaging>                                Type of package [default: jar].
  --properties.project.build.finalName=<finalName>                          Name of package [default: ${project.artifactId}-${project.version}]
  --properties.project.build.directory=<directory>                          Build root directory [default: target].
  --properties.project.build.sourceDirectory=<sourceDirectory>              Source directory [default: ${project.basedir}/src/main/java].
  --properties.project.build.scriptSourceDirectory=<scriptSourceDirectory>  Script source directory [default: src/main/scripts].
  --properties.project.build.testSourceDirectory=<testSourceDirectory>      Test source directory [default: ${project.basedir}/src/test/java].
  --properties.project.build.outputDirectory=<outputDirectory>              Classes output directory [default: ${project.build.directory}/classes].
  --properties.project.build.testOutputDirectory=<testOutputDirectory>      Test classes output directory [default: ${project.build.directory}/test-classes].
  --properties.project.build.sourceEncoding=<sourceEncoding>                Source encoding [default: UTF-8].
  --resources.default=<resources.default>    Default resources root directory [default: ${project.basedir}/src/main/resources]
  --resources.test=<resources.test>          Test resources root directory [default: ${project.basedir}/src/test/resources]

"""
from docopt import docopt

from ant2mvn import logger
from ant2mvn import mvn


log = logger.get_logger(__name__)


def main():
    args = docopt(__doc__, version='1.0.0')
    log.debug(args)

    libs = args['<libs>']

    pom_options = {
        'project': {
            'groupId': args['--project.groupId'],
            'artifactId': args['--project.artifactId'],
            'version': args['--project.version']
        },
        'repo': {
            'name': args['--repo.name'],
            'host': args['--repo.host'],
            'port': args['--repo.port']
        },
        'local_dependencies': {
            'default': {
                'groupId': args['--local.dependencies.default.groupId'],
                'version': args['--local.dependencies.default.version']
            }
        },
        'properties': {
            'project.packaging': args['--properties.project.packaging'],
            'project.build.finalName': args['--properties.project.build.finalName'],
            'project.build.directory': args['--properties.project.build.directory'],
            'project.build.sourceDirectory': args['--properties.project.build.sourceDirectory'],
            'project.build.scriptSourceDirectory': args['--properties.project.build.scriptSourceDirectory'],
            'project.build.testSourceDirectory': args['--properties.project.build.testSourceDirectory'],
            'project.build.outputDirectory': args['--properties.project.build.outputDirectory'],
            'project.build.testOutputDirectory': args['--properties.project.build.testOutputDirectory'],
            'project.build.sourceEncoding': args['--properties.project.build.sourceEncoding']
        },
        'resources': {
            'default': args['--resources.default'],
            'test': args['--resources.test']
        }
    }

    mvn.jar2pom(libs, local_dep_dir=args['--local.dependencies.dest'], pom_options=pom_options)


if __name__ == '__main__':
    main()
