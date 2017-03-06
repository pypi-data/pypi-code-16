# Copyright 2016 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from fresco import GET, Route, Response
from fresco.exceptions import NotFound

from fresco.util.urls import normpath as url_normpath

__version__ = '0.1.1'


class FSResources(object):

    def __init__(self,
                 search_path,
                 search_extensions=[],
                 directory_indexes=[],
                 rewriter=None,
                 responder=None,
                 route_name=None):
        """
        :param search_path: List of directories to search for content
        :param search_extensions: List of extensions to append to path
                                  (eg ``['.txt', '.md']`` etc). An extension
                                  will always be added, so if you want to be
                                  able to have the extension in the url you
                                  need to have ``''`` at the start of the list,
                                  eg ``['', '.htm', '.html']``.
        :param directory_indexes: List of default directory index filenames
                                  (eg ``['index.txt', 'readme.txt']`` etc)
        :param rewriter: Function that takes a virtual path and returns
                         a list of virtual paths to serve.
        :param responder: Function that takes a file path and returns a
                          response (or None if the file can't be served).
        :param route_name: passed as the 'name' argument to fresco.routing.Route
        """
        self.search_path = search_path
        self.rewriter = rewriter
        self.directory_indexes = directory_indexes
        self.search_extensions = [(ext if ext.startswith('.') else '.' + ext)
                                  for ext in search_extensions]
        self.responder = responder
        self.route_name = route_name

    @property
    def __routes__(self):
        return [
            Route('/<path:path>', GET, 'serve_path', name=self.route_name),
            Route('/', GET, 'serve_path', path='')]

    def serve_path(self, path=''):
        for action, path in self.get_candidate_paths(path):
            if action == 'redirect':
                return Response.redirect(path)
            elif action == 'serve':
                response = self.responder(path)
                if response is not None:
                    return response
            elif action == 'index':
                if self.make_index:
                    response = self.make_index(path)
                if response is not None:
                    return response
        raise NotFound()

    def get_candidate_paths(self,
                            virtual_path,
                            pjoin=os.path.join,
                            isdir=os.path.isdir,
                            isfile=os.path.isfile):
        virtual_path = url_normpath(virtual_path)
        if self.rewriter:
            virtual_paths = self.rewriter(virtual_path)
        else:
            virtual_paths = [virtual_path]
        for virtual_path in virtual_paths:
            for d in self.search_path:
                for ext in self.search_extensions:
                    fspath = pjoin(d, virtual_path) + ext
                    if isfile(fspath):
                        yield 'serve', fspath
                    elif isdir(fspath):
                        if fspath.endswith('/') or virtual_path == '':
                            for default in self.directory_indexes:
                                p = pjoin(fspath, default)
                                if isfile(p):
                                    yield 'serve', p
                            yield 'index', p
                        else:
                            yield 'redirect', virtual_path + '/'
