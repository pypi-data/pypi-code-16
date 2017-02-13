# -*- coding: utf-8 -*-


# Copyright (c) 2016  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Petr Šabata <contyk@redhat.com>

"""Module metadata manipulation library.

A python library for manipulation of the proposed module metadata format.

Example usage:

.. code:: python

    import modulemd
    mmd = modulemd.ModuleMetadata()
    mmd.load("metadata.yaml")
    mmd.add_module_license("ISC")
    mmd.components.clear_rpms()
    mmd.components.add_rpm("example", "with reason", multilib=["x86_64"])
    mmd.dump("out.yaml")
"""

import sys
import yaml

if sys.version_info > (3,):
    long = int

from modulemd.components import ModuleComponents
from modulemd.components.module import ModuleComponentModule
from modulemd.components.rpm import ModuleComponentRPM
from modulemd.api import ModuleAPI
from modulemd.filter import ModuleFilter
from modulemd.profile import ModuleProfile

supported_mdversions = ( 1, )

class ModuleMetadata(object):
    """Class representing the whole module."""

    REPODATA_FILENAME = "modulemd"

    def __init__(self):
        """Creates a new ModuleMetadata instance."""
        self.mdversion = max(supported_mdversions)
        self.name = ""
        self.stream = ""
        self.version = 0
        self.summary = ""
        self.description = ""
        self.module_licenses = set()
        self.content_licenses = set()
        self.buildrequires = dict()
        self.requires = dict()
        self.community = ""
        self.documentation = ""
        self.tracker = ""
        self.xmd = dict()
        self.profiles = dict()
        self.api = ModuleAPI()
        self.filter = ModuleFilter()
        self.components = ModuleComponents()

    def __repr__(self):
        return ("<ModuleMetadata: "
                "mdversion: {0}, "
                "name: {1}, "
                "stream: {2}, "
                "version: {3}, "
                "summary: {4}, "
                "description: {5}, "
                "module_licenses: {6}, "
                "content_licenses: {7}, "
                "buildrequires: {8}, "
                "requires: {9}, "
                "community: {10}, "
                "documentation: {11}, "
                "tracker: {12}, "
                "xmd: {13}, "
                "profiles: {14}, "
                "api: {15}, "
                "filter: {16}, "
                "components: {17}>").format(
                        repr(self.mdversion),
                        repr(self.name),
                        repr(self.stream),
                        repr(self.version),
                        repr(self.summary),
                        repr(self.description),
                        repr(sorted(self.module_licenses)),
                        repr(sorted(self.content_licenses)),
                        repr(self.buildrequires),
                        repr(self.requires),
                        repr(self.community),
                        repr(self.documentation),
                        repr(self.tracker),
                        repr(self.xmd),
                        repr(self.profiles),
                        repr(self.api),
                        repr(self.filter),
                        repr(self.components)
                )

    def load(self, f):
        """Loads a metadata file into the instance.

        :param str f: File name to load
        """
        with open(f, "r") as infile:
            data = infile.read()
        self.loads(data)

    def loads(self, s):
        """Loads metadata from a string.

        :param str s: Raw metadata in YAML
        :raises ValueError: If the metadata is invalid or unsupported.
        """
        yml = yaml.safe_load(s)
        if "document" not in yml or yml["document"] != "modulemd":
            raise ValueError("The supplied data isn't a valid modulemd document")
        if "version" not in yml:
            raise ValueError("Document version is required")
        if yml["version"] not in supported_mdversions:
            raise ValueError("The supplied metadata version isn't supported")
        self.mdversion = yml["version"]
        if "data" not in yml or not isinstance(yml["data"], dict):
            raise ValueError("Data section missing or mangled")
        if "name" in yml["data"]:
            self.name = str(yml["data"]["name"]).strip()
        if "stream" in yml["data"]:
            self.stream = str(yml["data"]["stream"]).strip()
        if "version" in yml["data"]:
            self.version = int(yml["data"]["version"])
        if "summary" in yml["data"]:
            self.summary = str(yml["data"]["summary"]).strip()
        if "description" in yml["data"]:
            self.description = str(yml["data"]["description"]).strip()
        if ("license" in yml["data"]
                and isinstance(yml["data"]["license"], dict)
                and "module" in yml["data"]["license"]
                and yml["data"]["license"]["module"]):
            self.module_licenses = set(yml["data"]["license"]["module"])
        if ("license" in yml["data"]
                and isinstance(yml["data"]["license"], dict)
                and "content" in yml["data"]["license"]):
            self.content_licenses = set(yml["data"]["license"]["content"])
        if ("dependencies" in yml["data"]
                and isinstance(yml["data"]["dependencies"], dict)):
            if ("buildrequires" in yml["data"]["dependencies"]
                    and isinstance(yml["data"]["dependencies"]["buildrequires"], dict)):
                for n, s in yml["data"]["dependencies"]["buildrequires"].items():
                    self.add_buildrequires(str(n), str(s))
            if ("requires" in yml["data"]["dependencies"]
                    and isinstance(yml["data"]["dependencies"]["requires"], dict)):
                for n, s in yml["data"]["dependencies"]["requires"].items():
                    self.add_requires(str(n), str(s))
        if "references" in yml["data"] and yml["data"]["references"]:
            if "community" in yml["data"]["references"]:
                self.community = yml["data"]["references"]["community"]
            if "documentation" in yml["data"]["references"]:
                self.documentation = yml["data"]["references"]["documentation"]
            if "tracker" in yml["data"]["references"]:
                self.tracker = yml["data"]["references"]["tracker"]
        if "xmd" in yml["data"]:
            self.xmd = yml["data"]["xmd"]
        if ("profiles" in yml["data"]
                and isinstance(yml["data"]["profiles"], dict)):
            for profile in yml["data"]["profiles"].keys():
                self.profiles[profile] = ModuleProfile()
                if "description" in yml["data"]["profiles"][profile]:
                    self.profiles[profile].description = \
                        str(yml["data"]["profiles"][profile]["description"])
                if "rpms" in yml["data"]["profiles"][profile]:
                    self.profiles[profile].rpms = \
                        set(yml["data"]["profiles"][profile]["rpms"])
        if ("api" in yml["data"]
                and isinstance(yml["data"]["api"], dict)):
            self.api = ModuleAPI()
            if ("rpms" in yml["data"]["api"]
                    and isinstance(yml["data"]["api"]["rpms"],list)):
                self.api.rpms = set(yml["data"]["api"]["rpms"])
        if ("filter" in yml["data"]
                and isinstance(yml["data"]["filter"], dict)):
            self.filter = ModuleFilter()
            if ("rpms" in yml["data"]["filter"]
                    and isinstance(yml["data"]["filter"]["rpms"],list)):
                self.filter.rpms = set(yml["data"]["filter"]["rpms"])
        if ("components" in yml["data"]
                and isinstance(yml["data"]["components"], dict)):
            self.components = ModuleComponents()
            if "rpms" in yml["data"]["components"]:
                for p, e in yml["data"]["components"]["rpms"].items():
                    extras = dict()
                    extras["rationale"] = e["rationale"]
                    if "buildorder" in e:
                        extras["buildorder"] = int(e["buildorder"])
                    if "repository" in e:
                        extras["repository"] = str(e["repository"])
                    if "cache" in e:
                        extras["cache"] = str(e["cache"])
                    if "ref" in e:
                        extras["ref"] = str(e["ref"])
                    if ("arches" in e
                            and isinstance(e["arches"], list)):
                        extras["arches"] = set(str(x) for x in e["arches"])
                    if ("multilib" in e
                            and isinstance(e["multilib"], list)):
                        extras["multilib"] = set(str(x) for x in e["multilib"])
                    self.components.add_rpm(p, **extras)
            if "modules" in yml["data"]["components"]:
                for p, e in yml["data"]["components"]["modules"].items():
                    extras = dict()
                    extras["rationale"] = e["rationale"]
                    if "buildorder" in e:
                        extras["buildorder"] = int(e["buildorder"])
                    if "repository" in e:
                        extras["repository"] = str(e["repository"])
                    if "ref" in e:
                        extras["ref"] = str(e["ref"])
                    self.components.add_module(p, **extras)

    def dump(self, f):
        """Dumps the metadata into the supplied file.

        :param str f: File name of the destination
        """
        data = self.dumps()
        with open(f, "w") as outfile:
            outfile.write(data)

    def dumps(self):
        """Dumps te metadata into a string.

        :rtype: str
        """
        data = dict()
        # header
        data["document"] = "modulemd"
        data["version"] = self.mdversion
        # data
        data["data"] = dict()
        data["data"]["name"] = self.name
        data["data"]["stream"] = self.stream
        data["data"]["version"] = self.version
        data["data"]["summary"] = self.summary
        data["data"]["description"] = self.description
        data["data"]["license"] = dict()
        data["data"]["license"]["module"] = list(self.module_licenses)
        if self.content_licenses:
            data["data"]["license"]["content"] = list(self.content_licenses)
        if self.buildrequires or self.requires:
            data["data"]["dependencies"] = dict()
            if self.buildrequires:
                data["data"]["dependencies"]["buildrequires"] = self.buildrequires
            if self.requires:
                data["data"]["dependencies"]["requires"] = self.requires
        if self.community or self.documentation or self.tracker:
            data["data"]["references"] = dict()
            if self.community:
                data["data"]["references"]["community"] = self.community
            if self.documentation:
                data["data"]["references"]["documentation"] = self.documentation
            if self.tracker:
                data["data"]["references"]["tracker"] = self.tracker
        if self.xmd:
            data["data"]["xmd"] = self.xmd
        if self.profiles:
            data["data"]["profiles"] = dict()
            for profile in self.profiles.keys():
                if self.profiles[profile].description:
                    if profile not in data["data"]["profiles"]:
                        data["data"]["profiles"][profile] = dict()
                    data["data"]["profiles"][profile]["description"] = \
                        str(self.profiles[profile].description)
                if self.profiles[profile].rpms:
                    if profile not in data["data"]["profiles"]:
                        data["data"]["profiles"][profile] = dict()
                    data["data"]["profiles"][profile]["rpms"] = \
                        list(self.profiles[profile].rpms)
        if self.api:
            data["data"]["api"] = dict()
            if self.api.rpms:
                data["data"]["api"]["rpms"] = list(self.api.rpms)
        if self.filter:
            data["data"]["filter"] = dict()
            if self.filter.rpms:
                data["data"]["filter"]["rpms"] = list(self.filter.rpms)
        if self.components:
            data["data"]["components"] = dict()
            if self.components.rpms:
                data["data"]["components"]["rpms"] = dict()
                for p in self.components.rpms.values():
                    extra = dict()
                    extra["rationale"] = p.rationale
                    if p.buildorder:
                        extra["buildorder"] = p.buildorder
                    if p.repository:
                        extra["repository"] = p.repository
                    if p.ref:
                        extra["ref"] = p.ref
                    if p.cache:
                        extra["cache"] = p.cache
                    if p.arches:
                        extra["arches"] = list(p.arches)
                    if p.multilib:
                        extra["multilib"] = list(p.multilib)
                    data["data"]["components"]["rpms"][p.name] = extra
            if self.components.modules:
                data["data"]["components"]["modules"] = dict()
                for p in self.components.modules.values():
                    extra = dict()
                    extra["rationale"] = p.rationale
                    if p.buildorder:
                        extra["buildorder"] = p.buildorder
                    if p.repository:
                        extra["repository"] = p.repository
                    if p.ref:
                        extra["ref"] = p.ref
                    data["data"]["components"]["modules"][p.name] = extra
        return yaml.safe_dump(data)

    @property
    def mdversion(self):
        """An int property representing the metadata format version used.

        This is automatically set to the highest supported version for
        new objects or set by the loaded document.  This value can be
        changed to one of the supported_mdversions to alter the output
        format.
        """
        return self._mdversion

    @mdversion.setter
    def mdversion(self, i):
        if not isinstance(i, (int, long)):
            raise TypeError("mdversion: data type not supported")
        if i not in supported_mdversions:
            raise ValueError("mdversion: document version not supported")
        self._mdversion = int(i)

    @property
    def name(self):
        """A string property representing the name of the module."""
        return self._name

    @name.setter
    def name(self, s):
        if not isinstance(s, str):
            raise TypeError("name: data type not supported")
        self._name = s

    @property
    def stream(self):
        """A string property representing the stream name of the module."""
        return self._stream

    @stream.setter
    def stream(self, s):
        if not isinstance(s, str):
            raise TypeError("stream: data type not supported")
        self._stream = str(s)

    @property
    def version(self):
        """An integer property representing the version of the module."""
        return self._version

    @version.setter
    def version(self, i):
        if not isinstance(i, (int, long)):
            raise TypeError("version: data type not supported")
        if i < 0:
            raise ValueError("version: version cannot be negative")
        self._version = i

    @property
    def summary(self):
        """A string property representing a short summary of the module."""
        return self._summary

    @summary.setter
    def summary(self, s):
        if not isinstance(s, str):
            raise TypeError("summary: data type not supported")
        self._summary = s

    @property
    def description(self):
        """A string property representing a detailed description of the
        module."""
        return self._description

    @description.setter
    def description(self, s):
        if not isinstance(s, str):
            raise TypeError("description: data type not supported")
        self._description = s

    @property
    def module_licenses(self):
        """A set of strings, a property, representing the license terms
        of the module itself."""
        return self._module_licenses

    @module_licenses.setter
    def module_licenses(self, ss):
        if not isinstance(ss, set):
            raise TypeError("module_licenses: data type not supported")
        for s in ss:
            if not isinstance(s, str):
                raise TypeError("module_licenses: data type not supported")
        self._module_licenses = ss

    def add_module_license(self, s):
        """Adds a module license to the set.

        :param str s: License name
        """
        if not isinstance(s, str):
            raise TypeError("add_module_license: data type not supported")
        self._module_licenses.add(s)

    def del_module_license(self, s):
        """Removes the supplied license from the module licenses set.

        :param str s: License name
        """
        if not isinstance(s, str):
            raise TypeError("del_module_license: data type not supported")
        self._module_licenses.discard(s)

    def clear_module_licenses(self):
        """Clears the module licenses set."""
        self._module_licenses.clear()

    @property
    def content_licenses(self):
        """A set of strings, a property, representing the license terms
        of the module contents."""
        return self._content_licenses

    @content_licenses.setter
    def content_licenses(self, ss):
        if not isinstance(ss, set):
            raise TypeError("content_licenses: data type not supported")
        for s in ss:
            if not isinstance(s, str):
                raise TypeError("content_licenses: data type not supported")
        self._content_licenses = ss

    def add_content_license(self, s):
        """Adds a content license to the set.

        :param str s: License name
        """
        if not isinstance(s, str):
            raise TypeError("add_content_license: data type not supported")
        self._content_licenses.add(s)

    def del_content_license(self, s):
        """Removes the supplied license from the content licenses set.

        :param str s: License name
        """
        if not isinstance(s, str):
            raise TypeError("del_content_license: data type not supported")
        self._content_licenses.discard(s)

    def clear_content_licenses(self):
        """Clears the content licenses set."""
        self._content_licenses.clear()

    @property
    def requires(self):
        """A dictionary property representing the required dependencies of
        the module.

        Keys are the required module names (strings), values are their
        required stream names (also strings).
        """
        return self._requires

    @requires.setter
    def requires(self, d):
        if not isinstance(d, dict):
            raise TypeError("requires: data type not supported")
        for k, v in d.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise TypeError("requires: data type not supported")
        self._requires = d

    def add_requires(self, n, v):
        """Adds a required module dependency.

        :param str n: Required module name
        :param str v: Required module stream name
        """
        if not isinstance(n, str) or not isinstance(v, str):
            raise TypeError("add_requires: data type not supported")
        self._requires[n] = v

    update_requires = add_requires

    def del_requires(self, n):
        """Deletes the dependency on the supplied module.

        :param str n: Required module name
        """
        if not isinstance(n, str):
            raise TypeError("del_requires: data type not supported")
        if n in self._requires:
            del self._requires[n]

    def clear_requires(self):
        """Removes all required runtime dependencies."""
        self._requires.clear()

    @property
    def buildrequires(self):
        """A dictionary property representing the required build dependencies
        of the module.

        Keys are the required module names (strings), values are their
        required stream names (also strings).
        """
        return self._buildrequires

    @buildrequires.setter
    def buildrequires(self, d):
        if not isinstance(d, dict):
            raise TypeError("buildrequires: data type not supported")
        for k, v in d.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise TypeError("buildrequires: data type not supported")
        self._buildrequires = d

    def add_buildrequires(self, n, v):
        """Adds a module build dependency.

        :param str n: Required module name
        :param str v: Required module stream name
        """
        if not isinstance(n, str) or not isinstance(v, str):
            raise TypeError("add_buildrequires: data type not supported")
        self._buildrequires[n] = v

    update_buildrequires = add_buildrequires

    def del_buildrequires(self, n):
        """Deletes the build dependency on the supplied module.

        :param str n: Required module name
        """
        if not isinstance(n, str):
            raise TypeError("del_buildrequires: data type not supported")
        if n in self._buildrequires:
            del self._buildrequires[n]

    def clear_buildrequires(self):
        """Removes all build dependencies."""
        self._buildrequires.clear()

    @property
    def community(self):
        """A string property representing a link to the upstream community
        for this module.
        """
        return self._community

    @community.setter
    def community(self, s):
        # TODO: Check if it looks like a link, unless empty
        if not isinstance(s, str):
            raise TypeError("community: data type not supported")
        self._community = s

    @property
    def documentation(self):
        """A string property representing a link to the upstream
        documentation for this module.
        """
        return self._documentation

    @documentation.setter
    def documentation(self, s):
        # TODO: Check if it looks like a link, unless empty
        if not isinstance(s, str):
            raise TypeError("documentation: data type not supported")
        self._documentation = s

    @property
    def tracker(self):
        """A string property representing a link to the upstream bug tracker
        for this module.
        """
        return self._tracker

    @tracker.setter
    def tracker(self, s):
        # TODO: Check if it looks like a link, unless empty
        if not isinstance(s, str):
            raise TypeError("tracker: data type not supported")
        self._tracker = s

    @property
    def xmd(self):
        """A dictionary property containing user-defined data."""
        return self._xmd

    @xmd.setter
    def xmd(self, d):
        if not isinstance(d, dict):
            raise TypeError("xmd: data type not supported")
        self._xmd = d

    @property
    def profiles(self):
        """A dictionary property representing the module profiles."""
        return self._profiles

    @profiles.setter
    def profiles(self, d):
        if not isinstance(d, dict):
            raise TypeError("profiles: data type not supported")
        for k, v in d.items():
            if not isinstance(k, str) or not isinstance(v, ModuleProfile):
                raise TypeError("profiles: data type not supported")
        self._profiles = d

    @property
    def api(self):
        """A ModuleAPI instance representing the module's public API."""
        return self._api

    @api.setter
    def api(self, o):
        if not isinstance(o, ModuleAPI):
            raise TypeError("api: data type not supported")
        self._api = o

    @property
    def filter(self):
        """A ModuleFilter instance representing the module's filter."""
        return self._filter

    @filter.setter
    def filter(self, o):
        if not isinstance(o, ModuleFilter):
            raise TypeError("filter: data type not supported")
        self._filter = o

    @property
    def components(self):
        """A ModuleComponents instance property representing the components
        defining the module.
        """
        return self._components

    @components.setter
    def components(self, o):
        if not isinstance(o, ModuleComponents):
            raise TypeError("components: data type not supported")
        self._components = o
