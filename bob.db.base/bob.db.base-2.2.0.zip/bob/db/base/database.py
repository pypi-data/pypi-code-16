#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os

from . import utils

from .file import File


class Database(object):
    """Low-level Database API to be used within bob."""

    def check_parameters_for_validity(self, parameters, parameter_description,
                                      valid_parameters, default_parameters=None):
        """Checks the given parameters for validity.

        Checks a given parameter is in the set of valid parameters. It also
        assures that the parameters form a tuple or a list.  If parameters is
        'None' or empty, the default_parameters will be returned (if
        default_parameters is omitted, all valid_parameters are returned).

        This function will return a tuple or list of parameters, or raise a
        ValueError.


        Parameters:

          parameters : str, [str] or None
            The parameters to be checked. Might be a string, a list/tuple of
            strings, or None.

          parameter_description : str
            A short description of the parameter. This will be used to raise an
            exception in case the parameter is not valid.

          valid_parameters : [str]
            A list/tuple of valid values for the parameters.

          default_parameters : [str] or None
            The list/tuple of default parameters that will be returned in case
            parameters is None or empty. If omitted, all valid_parameters are
            used.

        """

        if parameters is None:
            # parameters are not specified, i.e., 'None' or empty lists
            parameters = default_parameters if default_parameters is not None else valid_parameters

        if not isinstance(parameters, (list, tuple, set)):
            # parameter is just a single element, not a tuple or list -> transform it into a tuple
            parameters = (parameters,)

        # perform the checks
        for parameter in parameters:
            if parameter not in valid_parameters:
                raise ValueError("Invalid %s '%s'. Valid values are %s, or lists/tuples of those" % (parameter_description, parameter, valid_parameters))

        # check passed, now return the list/tuple of parameters
        return parameters

    def check_parameter_for_validity(self, parameter, parameter_description,
                                     valid_parameters, default_parameter=None):
        """Checks the given parameter for validity

        Ensures a given parameter is in the set of valid parameters. If the
        parameter is ``None`` or empty, the value in ``default_parameter`` will
        be returned, in case it is specified, otherwise a :py:exc:`ValueError`
        will be raised.

        This function will return the parameter after the check tuple or list
        of parameters, or raise a :py:exc:`ValueError`.


        Parameters:

          parameter : str
            The single parameter to be checked. Might be a string or None.

          parameter_description : str
            A short description of the parameter. This will be used to raise an
            exception in case the parameter is not valid.

          valid_parameters : [str]
            A list/tuple of valid values for the parameters.

          default_parameters : [str] or None
            The default parameter that will be returned in case parameter is
            None or empty. If omitted and parameter is empty, a ValueError is
            raised.

        """

        if parameter is None:
            # parameter not specified ...
            if default_parameter is not None:
                # ... -> use default parameter
                parameter = default_parameter
            else:
                # ... -> raise an exception
                raise ValueError("The %s has to be one of %s, it might not be 'None'." % (parameter_description, valid_parameters))

        if isinstance(parameter, (list, tuple, set)):
            # the parameter is in a list/tuple ...
            if len(parameter) > 1:
                raise ValueError("The %s has to be one of %s, it might not be more than one (%s was given)." % (parameter_description, valid_parameters, parameter))
            # ... -> we take the first one
            parameter = parameter[0]

        # perform the check
        if parameter not in valid_parameters:
            raise ValueError("The given %s '%s' is not allowed. Please choose one of %s." % (parameter_description, parameter, valid_parameters))

        # tests passed -> return the parameter
        return parameter

    def convert_names_to_highlevel(self, names, low_level_names,
                                   high_level_names):
        """
        Converts group names from a low level to high level API

        This is useful for example when you want to return ``db.groups()`` for
        the :py:mod:`bob.bio.base`. Your instance of the database should
        already have ``low_level_names`` and ``high_level_names`` initialized.

        """

        if names is None:
            return None
        mapping = dict(zip(low_level_names, high_level_names))
        if isinstance(names, str):
            return mapping.get(names)
        return [mapping[g] for g in names]

    def convert_names_to_lowlevel(self, names, low_level_names,
                                  high_level_names):
        """ Same as convert_names_to_highlevel but on reverse """

        if names is None:
            return None
        mapping = dict(zip(high_level_names, low_level_names))
        if isinstance(names, str):
            return mapping.get(names)
        return [mapping[g] for g in names]

    def original_file_names(self, files):
        """original_file_names(files) -> paths

        Returns the full path of the original data of the given File objects.

        **Parameters:**

        files : [:py:class:`bob.db.base.File`]
          The list of file object to retrieve the original data file names for.

        **Returns:**

        paths : [str]
          The paths extracted for the files, in the same order.
        """
        assert self.original_directory is not None
        assert self.original_extension is not None
        return self.file_names(files, self.original_directory, self.original_extension)

    def file_names(self, files, directory, extension):
        """file_names(files, directory, extension) -> paths

        Returns the full path of the given File objects.

        **Parameters:**

        files : [:py:class:`bob.db.base.File`]
          The list of file object to retrieve the file names for.

        directory : str
          The base directory, where the files can be found.

        extension : str
          The file name extension to add to all files.

        **Returns:**

        paths : [str]
          The paths extracted for the files, in the same order.
        """
        # return the paths of the files, do not remove duplicates
        return [f.make_path(directory, extension) for f in files]

    def sort(self, files):
        """sort(files) -> sorted

        Returns a sorted version of the given list of File's (or other structures that define an 'id' data member).
        The files will be sorted according to their id, and duplicate entries will be removed.

        **Parameters:**

        files : [:py:class:`bob.bio.base.database.BioFile`]
          The list of files to be uniquified and sorted.

        **Returns:**

        sorted : [:py:class:`bob.bio.base.database.BioFile`]
          The sorted list of files, with duplicate `BioFile.id`\s being removed.
        """
        # sort files using their sort function
        sorted_files = sorted(files)
        # remove duplicates
        return [f for i, f in enumerate(sorted_files) if not i or sorted_files[i - 1].id != f.id]

    def original_file_name(self, file):
        """This function returns the original file name for the given File object.

        Keyword parameters:

        file : :py:class:`bob.bio.base.database.BioFile` or a derivative
          The File objects for which the file name should be retrieved

        Return value : str
          The original file name for the given File object
        """
        # check if directory is set
        if not self.original_directory or not self.original_extension:
            raise ValueError(
                "The original_directory and/or the original_extension were not specified in the constructor.")
        # extract file name
        file_name = file.make_path(self.original_directory, self.original_extension)
        if not self.check_existence or os.path.exists(file_name):
            return file_name
        raise ValueError("The file '%s' was not found. Please check the original directory '%s' and extension '%s'?" % (
            file_name, self.original_directory, self.original_extension))


class SQLiteDatabase(Database):
    """This class can be used for handling SQL databases.

    It opens an SQL database in a read-only mode and keeps it opened during the
    whole session.


    Parameters:

      sqlite_file : str
        The file name (including full path) of the SQLite file to read or
        generate.

      file_class : a class instance
        The ``File`` class, which needs to be derived from
        :py:class:`bob.db.base.File`. This is required to be able to
        :py:meth:`query` the databases later on.

    """

    def __init__(self, sqlite_file, file_class):
        self.m_sqlite_file = sqlite_file
        if not os.path.exists(sqlite_file):
            self.m_session = None
        else:
            self.m_session = utils.session_try_readonly('sqlite', sqlite_file)

        # assert the given file class is derived from the File class
        assert issubclass(file_class, File)
        self.m_file_class = file_class

    def __del__(self):
        """Closes the connection to the database."""

        if self.is_valid():
            # do some magic to close the connection to the database file
            try:
                # Since the dispose function re-creates a pool
                #   which might fail in some conditions, e.g., when this destructor is called during the exit of the python interpreter
                self.m_session.close()
                self.m_session.bind.dispose()
            except (TypeError, AttributeError, KeyError):
                # ... I can just ignore the according exception...
                pass

    def is_valid(self):
        """Returns if a valid session has been opened for reading the database.
        """

        return self.m_session is not None

    def assert_validity(self):
        """Raise a RuntimeError if the database back-end is not available."""

        if not self.is_valid():
            raise IOError("Database of type 'sqlite' cannot be found at expected location '%s'." % self.m_sqlite_file)

    def query(self, *args):
        """Creates a query to the database using the given arguments."""

        self.assert_validity()
        return self.m_session.query(*args)

    def files(self, ids, preserve_order=True):
        """Returns a list of ``File`` objects with the given file ids

        Parameters:

          ids : list, tuple
            The ids of the object in the database table "file". This object
            should be a python iterable (such as a tuple or list).

          preserve_order : bool
            If True (the default) the order of elements is preserved, but the
            execution time increases.


        Returns:

          list: a list (that may be empty) of ``File`` objects.

        """

        file_objects = self.query(self.m_file_class).filter(self.m_file_class.id.in_(ids))
        if not preserve_order:
            return list(file_objects)
        else:
            path_dict = {}
            for f in file_objects:
                path_dict[f.id] = f
            return [path_dict[id] for id in ids]

    def paths(self, ids, prefix=None, suffix=None, preserve_order=True):
        """Returns a full file paths considering particular file ids


        Parameters:

          ids : list, tuple
            The ids of the object in the database table "file". This object
            should be a python iterable (such as a tuple or list).

          prefix : str or None
            The bit of path to be prepended to the filename stem

          suffix : str or None
            The extension determines the suffix that will be appended to the
            filename stem.

          preserve_order : bool
            If True (the default) the order of elements is preserved, but the
            execution time increases.


        Returns:

          list: A list (that may be empty) of the fully constructed paths given
          the file ids.

        """

        file_objects = self.files(ids, preserve_order)
        return [f.make_path(prefix, suffix) for f in file_objects]

    def reverse(self, paths, preserve_order=True):
        """Reverses the lookup from certain paths, returns a list of
        :py:class:`File`'s

        Parameters:

          paths : [str]
            The filename stems to query for. This object should be a python
            iterable (such as a tuple or list)

          preserve_order : True
            If True (the default) the order of elements is preserved, but the
            execution time increases.

        Returns:

          list: A list (that may be empty).

        """

        file_objects = self.query(self.m_file_class).filter(self.m_file_class.path.in_(paths))
        if not preserve_order:
            return file_objects
        else:
            # path_dict = {f.path : f for f in file_objects}  <<-- works fine with python 2.7, but not in 2.6
            path_dict = {}
            for f in file_objects:
                path_dict[f.path] = f
            return [path_dict[path] for path in paths]

    def uniquify(self, file_list):
        """Sorts the given list of File objects and removes duplicates from it.


        Parameters:

            file_list: [:py:class:`File`]
              A list of File objects to be handled. Also other objects can be
              handled, as long as they are sortable.

        Returns:

            list: A sorted copy of the given ``file_list`` with the duplicates
              removed.

        """

        return sorted(set(file_list))

    def all_files(self, **kwargs):
        """Returns the list of all File objects that satisfy your query.

        For possible keyword arguments, please check the implemention's
        ``objects()`` method.
        """

        return self.uniquify(self.objects(**kwargs))
