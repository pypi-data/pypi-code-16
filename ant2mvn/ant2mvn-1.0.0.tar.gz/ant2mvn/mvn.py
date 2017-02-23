# -*- coding: utf-8 -*-

from jinja2 import Environment, PackageLoader

import os
import re

from ant2mvn import utils


def jar2pom(jar_dir, local_dep_dir='lib', pom_options=None):

    if not pom_options:
        pom_options = {
            'project': {
                'groupId': 'com.example',
                'artifactId': 'artifact-example',
                'version': '1.0.0'
            },
            'repo': {
                'name': 'maven_central_repo',
                'host': 'search.maven.org'
            },
            'local_dependencies': {
                'default': {
                    'groupId': 'com.qq.utest.x',
                    'version': '1.0.0'
                }
            },
            'properties': {
                'project.packaging': 'jar',
                'project.build.finalName': '${project.artifactId}-${project.version}',
                'project.build.directory': 'target',
                'project.build.sourceDirectory': '${project.basedir}/src/main/java',
                'project.build.scriptSourceDirectory': 'src/main/scripts',
                'project.build.testSourceDirectory': '${project.basedir}/src/test/java',
                'project.build.outputDirectory': 'target/classes',
                'project.build.testOutputDirectory': '${project.build.directory}/test-classes',
                'project.build.sourceEncoding': 'UTF-8'
            },
            'resources': {
                'default': '${project.basedir}/src/main/resources',
                'test': '${project.basedir}/src/test/resources'
            }
        }

    jars = utils.get_files(jar_dir, '.jar')

    if len(jars) <= 0:
        return

    if not os.path.exists(local_dep_dir):
        os.makedirs(local_dep_dir)

    local_dep_pattern = re.compile(r"(.*?)-(\d[\.\-\w]*)\.jar")

    dependencies = []
    local_dependencies = []

    for jar_path in jars:
        with open(jar_path, 'rb') as jar_content:
            s = utils.sha1(jar_content.read())

            api = utils.MavenCentralRepoRestSearchApi(pom_options['repo']['name'], pom_options['repo']['host'])
            response = api.sha1_search(s)

            docs = response['response']['docs']

            if len(docs) > 0:
                d = docs[0]

                artifact = d.get('id').split(':')

                dependencies.append({
                    'groupId': artifact[0],
                    'artifactId': artifact[1],
                    'version': artifact[2],
                })
            else:
                local_jar_name = os.path.basename(jar_path)
                dest_jar_path = '%s/%s' % (local_dep_dir, local_jar_name)

                with open(dest_jar_path, 'wb') as lib:
                    lib.write(jar_content.read())

                g = pom_options['local_dependencies']['default']['groupId']
                p = dest_jar_path

                m = local_dep_pattern.match(local_jar_name)
                if m:
                    a = m.group(1)
                    v = m.group(2)
                else:
                    a = local_jar_name
                    v = pom_options['local_dependencies']['default']['version']

                local_dependencies.append({
                    'groupId': g,
                    'artifactId': a,
                    'version': v,
                    'path': p if p.startswith('/') else '${project.basedir}/%s' % p
                })

    env = Environment(loader=PackageLoader('ant2mvn', 'templates'))

    print(env.get_template('pom.xml.template').render(
        project={
            'groupId': pom_options['project']['groupId'],
            'artifactId': pom_options['project']['artifactId'],
            'version': pom_options['project']['version']
        },
        dependencies=dependencies,
        local_dependencies=local_dependencies,
        properties=pom_options['properties'],
        resources=pom_options['resources']
    ))

