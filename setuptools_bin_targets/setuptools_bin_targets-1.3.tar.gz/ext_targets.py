import os
from distutils import log
from setuptools import Extension
from setuptools.extension import Library
from distutils.ccompiler import CCompiler
from distutils.dep_util import newer_group
from distutils.errors import DistutilsSetupError
from setuptools.command.build_ext import build_ext as _build_ext

class Executable(Extension):
    """
    This target will link the extension as a standalone application
    """
    libtype = 'static'
    target_desc = CCompiler.EXECUTABLE


class SharedLibrary(Library):
    """
    This target will link the extension as a static lib, eg lib.a
    """
    libtype = 'shared'
    target_desc = CCompiler.SHARED_LIBRARY


class StaticLibrary(Library):
    """
    This target will link the extension as a static lib, eg lib.a
    """
    libtype = 'static'


class build_ext(_build_ext):

    def get_ext_filename(self, fullname):
        if fullname in self.ext_map:
            ext = self.ext_map[fullname]
            if isinstance(ext, Library):
                return self.shlib_compiler.library_filename(fullname, ext.libtype)
            elif isinstance(ext, Executable):
                return self.shlib_compiler.executable_filename(fullname)
        return super(build_ext, self).get_ext_filename(fullname)

    def build_extension(self, ext):
        sources = ext.sources
        if sources is None or not isinstance(sources, (list, tuple)):
            raise DistutilsSetupError(
                  "in 'ext_modules' option (extension '%s'), "
                  "'sources' must be present and must be "
                  "a list of source filenames" % ext.name)
        sources = list(sources)

        ext_path = self.get_ext_fullpath(ext.name)

        depends = sources + ext.depends
        if not (self.force or newer_group(depends, ext_path, 'newer')):
            log.debug("skipping '%s' extension (up-to-date)", ext.name)
            return
        else:
            log.info("building '%s' extension", ext.name)

        # First, scan the sources for SWIG definition files (.i), run
        # SWIG on 'em to create .c files, and modify the sources list
        # accordingly.
        sources = self.swig_sources(sources, ext)

        # Next, compile the source code to object files.

        # XXX not honouring 'define_macros' or 'undef_macros' -- the
        # CCompiler API needs to change to accommodate this, and I
        # want to do one thing at a time!

        # Two possible sources for extra compiler arguments:
        #   - 'extra_compile_args' in Extension object
        #   - CFLAGS environment variable (not particularly
        #     elegant, but people seem to expect it and I
        #     guess it's useful)
        # The environment variable should take precedence, and
        # any sensible compiler will give precedence to later
        # command line args.  Hence we combine them in order:
        extra_args = ext.extra_compile_args or []

        macros = ext.define_macros[:]
        for undef in ext.undef_macros:
            macros.append((undef,))

        objects = self.compiler.compile(sources,
                                         output_dir=self.build_temp,
                                         macros=macros,
                                         include_dirs=ext.include_dirs,
                                         debug=self.debug,
                                         extra_postargs=extra_args,
                                         depends=ext.depends)

        # XXX outdated variable, kept here in case third-part code
        # needs it.
        self._built_objects = objects[:]

        # Now link the object files together into the desired target --
        # of course, first we have to figure out all the other things
        # that go into the mix.
        if ext.extra_objects:
            objects.extend(ext.extra_objects)
        extra_args = ext.extra_link_args or []

        # Detect target language, if not provided
        language = ext.language or self.compiler.detect_language(sources)

        if isinstance(ext, StaticLibrary):
            output_dir = os.path.dirname(ext_path)
            return self.compiler.create_static_lib(
                objects=objects,
                output_libname=ext.name,
                output_dir=output_dir,
                debug=self.debug,
                target_lang=language)

        else:
            # Allow replacing link arg -bundle with -dynamiclib (for osx)
            if '-dynamiclib' in extra_args:
                try:
                    self.compiler.linker_so.pop(self.compiler.linker_so.index('-bundle'))
                except (IndexError, ValueError):
                    pass

            return self.compiler.link(
                target_desc=ext.target_desc,
                objects=objects,
                output_filename=ext_path,
                libraries=self.get_libraries(ext),
                library_dirs=ext.library_dirs,
                runtime_library_dirs=ext.runtime_library_dirs,
                extra_postargs=extra_args,
                debug=self.debug,
                target_lang=language)
