
import os
# import glob
import hashlib
# import pdb
# import subprocess

import netCDF4
import numpy as np


class EasyTest(object):
    def __init__(self, exe, args=None, refdirectory=None, files=None, output_directory=None, checksum_exclude=[], basedir='.', switch_back = True, **kwargs):
        """
        Parameters
        ---------
        exe : str
            command that will be executed at shell
        args : list
            list with command line arguments to be appended to executable
        refdirectory : str
            reference data directory. From this directory, files will be
            searched recursively and all will be checked.
        files : list
            as an alternative, the file list can be provided directly
            then the refdirectory is ignored
        output_directory : str
            directory where the results of the simulations are expected
        checksum_exclude : list
            list of filename extensions which should be excluded from checksum analysis
            the background is that e.g. postscript or PDF files will always differ and
            the produce failures. Checking these file can be excluded.
            exxample: checksum_exclude=['ps','pdf']
        basedir : str
            name of directory where the tests will be executed
        switch_back : Bool
            if True, then directory is switched back to current directory after performing tests
        """
        self.exe = exe
        self.args = args
        self.refdirectory = refdirectory
        self.files2check = files
        self.output_directory = output_directory
        self.sucess = True
        self.checksum_exclude = checksum_exclude
        self.supported_extensions = ['nc']  # extensions supported for file content comparison

        self.basedir = basedir
        self._switch_back = switch_back

        if self.refdirectory is not None:
            assert self.files2check is None, 'Either the REFDIRECTORY or the FILELIST can be provided, but not both together'
            if self.refdirectory[-1] != os.sep:
                self.refdirectory += os.sep
        else:
            assert self.files2check is not None, 'Either the REFDIRECTORY or the FILELIST can be provided, but not both together'


        assert self.output_directory is not None, 'Output directory needs to be given!'
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        if self.output_directory[-1] != os.sep:
            self.output_directory += os.sep

    def run_tests(self, files=None, graphics=None, checksum_files=None, execute=True, check_size=None, check_file_content=None, check_size_gt_zero=None):
        """
        Execute program and run tests

        Parameters
        ----------
        files : list/str
            list of filenames to be checked.
            If 'all' is given instead, then the program automatically
            tries to check for all files which are found in the
            reference data directory
        graphics : None
            check if graphics are equal. Not implemented yet
        checksum_files : list/str
            list of filenames to be checked using MD5 checksum.
            If 'all' is given instead, then the program automatically
            tries to check for all files which are found in the
            reference data directory
        check_size : list/str
            same as for checksum, but for checking file sizes
        execute : bool
            run external program before performing tests
        check_file_content : list
            list with file extensions for which the content of the files should be checked
            currently supported options ['nc']
        check_size_gt_zero : bool
            if True, then all output files are checked to have sizes > 0 bytes
        """

        if execute:
            if self.exe is not None:
                self._execute()
            else:
                assert False, 'No executable specified!'

        if files is not None:
            if self.files2check is None:  # from reference directory
                files2test = self._get_reference_file_list(files)
                assert len(files2test) > 0, 'No testfiles were found in the reference directory! ' + self.refdirectory
                file_test = self._test_files(files2test)
            else:
                files2test = self.files2check
                file_test = self._test_files(files2test, replace_path=False)

        if graphics is not None:
            assert False, 'Graphic testing currently not implemented yet!'
            #self._test_graphics(self._get_graphic_list(graphics))

        if checksum_files is not None:
            assert self.files2check is None, 'CHECKSUM test can not be performed when no reference directory is used'
            files2testchk = self._get_reference_file_list(checksum_files)
            assert len(files2testchk) > 0, 'No testfiles were found in the reference directory for checksum! ' + self.refdirectory
            chk_test = self._test_checksum(files2testchk)

        if check_size is not None:
            assert self.files2check is None, 'CHECKSIZE test can not be performed when no reference directory is used'
            files2testsize = self._get_reference_file_list(check_size)
            assert len(files2testsize) > 0, 'No testfiles were found in the reference directory for check size! ' + self.refdirectory
            chk_size = self._test_filesize(files2testsize)

        if check_size_gt_zero is not None:
            if self.files2check is None:  # from reference directory
                files2test = self._get_reference_file_list(files)
                assert len(files2test) > 0, 'No testfiles were found in the reference directory! ' + self.refdirectory
            else:
                files2test = self.files2check
            chk_size0 = self._test_filesize_gt_0(files2test)

        if check_file_content is not None:
            chk_content = self._check_file_contents(check_file_content)

        if files is not None:
            if file_test:
                print 'File     ... SUCESSFULL'
            else:
                print 'File     ... FAILED'
                self.sucess = False

        if checksum_files is not None:
            if chk_test:
                print 'Checksum ... SUCESSFULL'
            else:
                print 'Checksum ... FAILED'
                self.sucess = False

        if check_size is not None:
            if chk_size:
                print('Check size ... SUCESSFULL')
            else:
                print('Check size ... FAILED')
                self.sucess = False

        if check_size_gt_zero is not None:
            if chk_size0:
                print('Check size > 0 ... SUCESSFULL')
            else:
                print('Check size > 0  ... FAILED')
                self.sucess = False

        if check_file_content is not None:
            if chk_content:
                print('Check content ... SUCESSFULL')
            else:
                print('Check content ... FAILED')
                self.sucess = False


    def _check_file_contents(self, exts):
        """
        Parameters
        ----------
        ext : list
            list with file extensions
        """
        # check that correct file formats are provided
        for k in exts:
            if k not in self.supported_extensions:
                print('File formate not supported yet for explicit comparison: %s' % k)
                assert False

        # now check file contents for each format
        sucess = True
        for k in exts:
            if k == 'nc':
                sucess = self._compare_netcdf_files()
            else:
                print('ERROR: unsupported file format, no checker implemented yet: %s' % k)
                sucess = False
        return sucess

    def _compare_netcdf_files(self):
        rfiles = self._get_reference_file_list('all')
        sucess = True
        for file1 in rfiles:
            if os.path.splitext(file1)[-1] == '.nc':
                file2 = file1.replace(self.refdirectory, self.output_directory)
                res = self._compare_netcdf(file1, file2)
                if res == False:
                    sucess = False
        return sucess

    def _compare_netcdf(self, f1, f2, compare_variables=True, compare_values=True, allow_subset=False):
        """
        compare content of two netCDF files
        if the two files have different lengths

        Parameters
        ----------
        allow_subset : bool
            allow that only a slice of the datasets is compared
        """
        F1 = netCDF4.Dataset(f1, mode='r')
        F2 = netCDF4.Dataset(f2, mode='r')

        sucess = True
        if compare_variables:
            res = self._compare_netcdf_variables(F1,F2)
            if res == False:
                sucess = False

        if compare_values:
            res = self._compare_netcdf_values(F1,F2, allow_subset=allow_subset)
            if res == False:
                sucess = False

        F1.close()
        F2.close()
        return sucess

    def _compare_netcdf_variables(self, F1, F2):
        """
        compare if two netCDF files have the same variables
        """
        sucess = True
        for k in F1.variables.keys():
            if k not in F2.variables.keys():
                print F1.variables.keys()
                print F2.variables.keys()
                print('Missing variable in one netCDF file: %s' % k)
                sucess = False
        return sucess


    def _compare_netcdf_values(self, F1, F2, allow_subset=False):
        """
        compare if two netCDF files have the same values
        """
        sucess = True
        for k in F1.variables.keys():
            x1 = F1.variables[k][:]
            x2 = F2.variables[k][:]

            n1 = len(x1)
            n2 = len(x2)

            if allow_subset:  # allow that only a subset of data is compared
                assert False
            else:
                if n1 == n2:
                    d = x1 - x2
                    res = np.all(d == 0.)
                else:
                    res = False

            if res == False:
                sucess = False

        return sucess

    def _get_reference_file_list(self, files):
        if type(files) is list:
            r = []
            for f in files:
                r.append(self.refdirectory + os.path.basename(f))
            return r
        else:
            if files == 'all':
                files = self._get_files_from_refdir()
            else:
                assert False, 'Argument FILES has not been correctly specified!'
        return files

    def _get_files_from_refdir(self):
        """ get list of files from reference directory """
        #return glob.glob(self.refdirectory + '*')
        # http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
        import fnmatch
        matches = []
        for root, dirnames, filenames in os.walk(self.refdirectory):
          for filename in fnmatch.filter(filenames, '*'):
            matches.append(os.path.join(root, filename))
        return matches

    def _get_graphic_list(self, files):
        assert False

    def _get_cmd_list(self):
        """
        get command list
        """
        r = ''
        r += self.exe
        for a in self.args:
            r += ' ' + a
        return r

    def _execute(self):
        """
        run the actual program

        generates a command line string for execution in a shell.
        and then executes the command

        Parameters
        ----------
        wdir : str
            working directory
        """

        self._change_wrk_dir()

        # execute command line
        cmd = self._get_cmd_list()
        print 'Running external process:'
        print '   Command line: ', cmd
        print '   Directory   : ', os.path.realpath(os.curdir)
        #subprocess.call(cmd, shell=True)  # todo use subprocess
        os.system(cmd)

        self._change_wkr_dir_back()


    def _change_wrk_dir(self):
        self._curdir = os.path.realpath(os.curdir)
        if self.basedir != '.':
            os.chdir(self.basedir)

    def _change_wkr_dir_back(self):
        if self._switch_back:
            os.chdir(self._curdir)


    def _test_files(self, reffiles, replace_path=True):
        """
        test availability of files

        Parameters
        ----------
        reffiles : list
            list of reference files to agains
        """
        res = True
        for f in reffiles:
            # get list of expected plot files
            if replace_path:
                sf = f.replace(self.refdirectory,self.output_directory)
            else:
                sf=f
            if os.path.exists(sf):
                pass
            else:
                res = False
                print 'Failure: ', sf
        return res

    def _test_graphics(self, reffiles):
        assert False


    def _test_filesize_gt_0(self, reffiles):
        """
        test that filesizes are all > 0 bytes

        Parameters
        ----------
        reffiles : list
            list of files to be processed
        """
        res = True
        for f in reffiles:
            # filesize in bytes
            s = os.path.getsize(f)
            if s > 0.:
                pass
            else:
                res = False
        return res


    def _test_filesize(self, reffiles):
        """
        test similarity of filesizes

        Parameters
        ----------
        reffiles : list
            list of files to be processed
        """
        res = True
        for f in reffiles:
            sf = f.replace(self.refdirectory, self.output_directory)

            # filesize in bytes
            s1 = os.path.getsize(f)
            s2 = os.path.getsize(sf)
            if s1 != s2:
                res = False
                print ''
                print('Filesize failure: %s, %s' % (s1,s2))
                print('File1: %s' % f)
                print('File2: %s' % sf)

        return res


    def _test_checksum(self, reffiles):
        """
        perform a checksum test for all reffiles given
        against the files in the current plot dir

        Parameters
        ----------
        reffiles : list
            list of files to be processed
        """

        res = True
        for f in reffiles:
            # exclude files that are in checksum_exclude list
            # e.g. it does not make sense to perform MD5 analysis of
            # postscript files as these have most likely always different
            # headers
            if os.path.splitext(f)[1][1:] in self.checksum_exclude:
                continue

            # calculate hash keys
            cref = self.hashfile(open(f, 'rb'), hashlib.sha256())
            sf = f.replace(self.refdirectory, self.output_directory)
            sfref = self.hashfile(open(sf, 'rb'), hashlib.sha256())

            if cref != sfref:
                print ''
                print 'Different sha256 key: ', os.path.basename(f), cref.encode('hex'), sfref.encode('hex')
                print sf
                print f
                res = False

        return res

    def hashfile(self, afile, hasher, blocksize=65536):
        """
        perform memory effiecient sha256 checksum on
        provided filename.
        See https://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file#3431835

        Parameters
        ----------
        afile : string
        hasher: hash function
        blocksize: file read chunk size
        """
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        return hasher.digest()
