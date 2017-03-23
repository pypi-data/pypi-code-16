# -*- coding: utf-8 -*-
'''CommonBuild Dependency Manager

Copyright (c) CERN 2015-2017

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Authors:
    T. Levens       <tom.levens@cern.ch>
    R. De Maria     <riccardo.de.maria@cern.ch>
'''

import glob
import importlib
import json
import logging
import os
import pickle
import requests
import shutil
import site
import six
import sys
import xml.etree.ElementTree as ET
import zipfile

if six.PY2:
    from urllib import urlretrieve, urlencode
else:
    from urllib.parse import urlencode
    from urllib.request import urlretrieve


class Manager(object):
    def __init__(self, pkg=None, lvl=None):
        logging.basicConfig()
        self.log = logging.getLogger(__package__)
        if lvl is not None:
            self.log.setLevel(lvl)
        if pkg is not None:
            if not self.is_registered(pkg):
                self.install(pkg)

    def set_logging_level(self, lvl):
        self.log.setLevel(lvl)

    def jar_path(self):
        '''Return the directory containing the jar files'''
        return os.path.join(self._dir(), 'lib')

    def jars(self):
        '''Return a list of all jar files'''
        if os.path.isdir(self.jar_path()):
            return [
                os.path.join(self.jar_path(), f)
                for f in os.listdir(self.jar_path())
                if f.lower().endswith('.jar')
            ]
        else:
            return []

    def class_list(self):
        '''List all classes in the resolved jar files'''
        classes = []
        for jar in self.jars():
            names = zipfile.ZipFile(jar).namelist()
            for name in names:
                if name.endswith('.class'):
                    classes.append(name[:-6].replace('/', '.'))
        return sorted(classes)

    def class_hints(self, class_name):
        '''Print python shortcuts for the class resolved in jar files

        Usage::

            import cmmnbuild_dep_manager
            mgr = cmmnbuild_dep_manager.Manager()
            jpype = mgr.start_jpype_jvm()
            print(mgr.class_hints('Fidel'))

        '''
        names = sorted(self.class_search(class_name))
        roots = set()
        for name in names:
            parts = name.split('.')
            cname = parts[-1]
            root = parts[0]
            if root not in roots:
                print('{0} = jpype.JPackage(\'{0}\')'.format(root))
                roots.add(root)
            print('{0} = {1}'.format(cname, name))

    def class_search(self, class_name):
        '''Search for classes in the class list'''
        return list(filter(lambda x: class_name in x, self.class_list()))

    def class_path(self, extra_jars=[]):
        '''Returns a delimited string suitable for java.class.path'''
        jars = self.jars()
        jars.extend(extra_jars)
        jars.append(os.getcwd())
        return ';'.join(jars) if os.name == 'nt' else ':'.join(jars)

    def start_jpype_jvm(self, extra_jars=[]):
        '''Starts a new JPype JVM with the appropriate class path'''
        import jpype
        if not jpype.isJVMStarted():
            self.log.info(
                'starting a JPype JVM with {0} jars from {1}'.format(
                    len(self.jars()),
                    self.jar_path()
                )
            )
            javalibpath = os.environ.get('JAVA_JVM_LIB')
            if javalibpath is None:
                javalibpath = jpype.getDefaultJVMPath()
            jpype.startJVM(
                javalibpath,
                '-Djava.class.path={0}'.format(self.class_path(extra_jars))
            )
            java_version = jpype.java.lang.System.getProperty('java.version')
            if not java_version.startswith('1.8'):
                raise OSError('Java version must be >1.8: {0} is {1}'.format(
                    javalibpath, java_version
                ))
        else:
            self.log.warning('JVM is already started')
        return jpype

    def _user_dir(self):
        return os.path.join(site.getusersitepackages(), __package__)

    def _dist_dir(self):
        return os.path.dirname(__file__)

    def _dir(self):
        if os.path.isdir(self._user_dir()):
            return self._user_dir()
        else:
            return self._dist_dir()

    def _load_modules(self):
        '''Load modules data'''
        modules = {}

        # Load pickled 'modules' files created by versions < 2.0.0
        old_mod_files = (
            os.path.join(self._dist_dir(), 'modules'),
            os.path.join(self._user_dir(), 'modules')
        )
        for f in old_mod_files:
            if os.path.isfile(f):
                self.log.debug('loading {0}'.format(f))
                with open(f, 'rb') as fp:
                    pkl_data = pickle.load(fp)
                    for k in pkl_data:
                        modules[k] = ''

        # Load json 'modules.json' files created by version >= 2.0.0
        mod_files = (
            os.path.join(self._dist_dir(), 'modules.json'),
            os.path.join(self._user_dir(), 'modules.json')
        )
        for f in mod_files:
            if os.path.isfile(f):
                self.log.debug('loading {0}'.format(f))
                with open(f, 'r') as fp:
                    json_data = json.load(fp)
                    for k, v in json_data.items():
                        modules[k] = v

        return modules

    def _save_modules(self, modules):
        '''Save modules data'''
        user_dir = self._user_dir()
        dist_dir = self._dist_dir()
        if os.path.isdir(user_dir):
            save_dir = user_dir
        elif os.access(dist_dir, os.W_OK | os.X_OK):
            save_dir = dist_dir
        else:
            self.log.info('creating directory {0}'.format(user_dir))
            os.makedirs(user_dir)
            save_dir = user_dir
        mod_file = os.path.join(save_dir, 'modules.json')
        self.log.debug('saving {0}'.format(mod_file))
        with open(mod_file, 'w') as fp:
            json.dump(modules, fp)

        # Remove 'modules' file used by versions < 2.0.0
        old_modules = os.path.join(save_dir, 'modules')
        if os.path.isfile(old_modules):
            self.log.warning('removing obsolete file {0}'.format(old_modules))
            os.remove(old_modules)

    def register(self, *args):
        '''Register a module'''
        ret = []
        modules = self._load_modules()
        for name in args:
            try:
                module = importlib.import_module(name)

                # Check __cmmnbuild_deps__ exists
                cmmnbuild_deps = None
                try:
                    cmmnbuild_deps = module.__cmmnbuild_deps__
                except:
                    pass
                try:
                    cmmnbuild_deps = module.cmmnbuild_deps
                    self.log.warning('{0} uses depreciated cmmnbuild_deps and '
                                     'should be updated'.format(name))
                except:
                    pass
                if cmmnbuild_deps is None:
                    raise AttributeError

                # Check __version__ exists
                version = module.__version__

                if name not in modules.keys() or modules[name] != version:
                    modules[name] = ''
                    self.log.info('{0} registered'.format(name))
                    ret.append(name)
            except ImportError:
                self.log.error(
                    '{0} not found'.format(name)
                )
            except AttributeError:
                self.log.error(
                    '{0}.__cmmnbuild_deps__ does not exist'.format(name)
                )
        if ret:
            self._save_modules(modules)
        return tuple(ret)

    def unregister(self, *args):
        '''Unregister a module'''
        ret = []
        modules = self._load_modules()
        for name in args:
            if name in modules.keys():
                del modules[name]
                self.log.info('{0} unregistered'.format(name))
                ret.append(name)
        if ret:
            self._save_modules(modules)
        return tuple(ret)

    def install(self, *args):
        '''Register a module and resolve dependencies'''
        ret = self.register(*args)
        if ret:
            self.resolve()
        return ret

    def uninstall(self, *args):
        '''Unregister a module and resolve dependencies'''
        ret = self.unregister(*args)
        if ret:
            self.resolve()
        return ret

    def is_registered(self, name):
        '''Check if module is registered'''
        modules = self._load_modules()
        if name in modules.keys():
            try:
                module = importlib.import_module(name)
                if modules[name] == module.__version__:
                    return True
            except:
                pass
        return False

    def list(self):
        '''Returns a list of the currently registered modules'''
        return sorted(self._load_modules().keys())

    def resolve(self):
        '''Resolve dependencies for all registered modules'''
        self.log.info('resolving dependencies')
        self.log.debug('lib directory is {0}'.format(self.jar_path()))

        deps = []
        modules = self._load_modules()

        # Build the dependency list from all installed packages
        for name, vers in modules.items():
            try:
                module = importlib.import_module(name)

                cmmnbuild_deps = None
                try:
                    cmmnbuild_deps = module.__cmmnbuild_deps__
                except:
                    pass
                try:
                    cmmnbuild_deps = module.cmmnbuild_deps
                    self.log.warning('{0} uses depreciated cmmnbuild_deps and '
                                     'should be updated'.format(name))
                except:
                    pass
                if cmmnbuild_deps is None:
                    raise AttributeError

                for dep in cmmnbuild_deps:
                    if isinstance(dep, str):
                        deps.append({'product': dep})
                    elif isinstance(dep, dict):
                        deps.append({str(k): str(v) for k, v in dep.items()})
                    else:
                        raise TypeError('{0}.__cmmnbuild_deps__ must be a list '
                                        'of str or dict'.format(name))
                    self.log.info('{0} has dependency {1}'.format(
                        name, deps[-1]['product']
                    ))
                modules[name] = module.__version__
            except ImportError:
                self.log.error('{0} not found'.format(name))
                self.unregister(name)
            except Exception as e:
                self.log.error(e)

        self._save_modules(modules)

        if not deps:
            self.log.error('no dependencies were found')
            return

        # Generate product.xml
        pxml = ET.Element('products')
        pxml_prod = ET.SubElement(pxml, 'product', attrib={
            'name': __package__,
            'version': sys.modules[__package__].__version__,
            'directory': ''
        })
        pxml_deps = ET.SubElement(pxml_prod, 'dependencies')

        for dep in deps:
            ET.SubElement(pxml_deps, 'dep', attrib=dep)

        # Post product.xml to CBNG web service
        self.log.info('resolving dependencies using CBNG web service: '
                      'https://wikis.cern.ch/display/DVTLS/CBNG+Web+service')

        resp = requests.post('http://bewww.cern.ch/ap/cbng-web/', urlencode({
            'action': 'get-deps',
            'product_xml': ET.tostring(pxml)
        })).json()

        if not resp['result']:
            raise Exception(resp['message'])

        self.log.info('CBNG results: {0}'.format(resp['data']['wd_url']))

        # Download archive file
        self.log.info('downloading archive: {0}'.format(
            resp['data']['lib_all_url']
        ))
        tmp_file, _ = urlretrieve(resp['data']['lib_all_url'])

        # Create user directory if dist directory is not writeable
        if not os.access(self._dist_dir(), os.W_OK | os.X_OK):
            if not os.path.exists(self._user_dir()):
                self.log.info('creating directory {0}'.format(
                    self._user_dir())
                )
                os.makedirs(self._user_dir())

        # Remove 'jars' directory used by versions < 2.0.0
        old_jars_dir = os.path.join(self._dir(), 'jars')
        if os.path.isdir(old_jars_dir):
            self.log.warning('removing obsolete directory {0}'.format(
                old_jars_dir
            ))
            shutil.rmtree(old_jars_dir)

        # Remove exisiting jars
        old_jars = glob.glob(os.path.join(self.jar_path(), '*.jar'))
        self.log.info('removing {0} jars from {1}'.format(
            len(old_jars), self.jar_path()
        ))
        for jar in old_jars:
            os.remove(jar)

        # Unzip jar archive
        zip_file = zipfile.ZipFile(tmp_file)
        for f in zip_file.namelist():
            if os.path.dirname(f) == 'lib':
                self.log.info('extracting {0}'.format(f))
                zip_file.extract(f, self._dir())
