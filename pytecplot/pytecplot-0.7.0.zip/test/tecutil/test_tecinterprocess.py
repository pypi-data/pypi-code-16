from __future__ import unicode_literals

import datetime
import logging
import os
import sys
import platform
import unittest

from os import path
from six import string_types
from tempfile import NamedTemporaryFile
from unittest.mock import patch, Mock, PropertyMock
from warnings import catch_warnings

import tecplot as tp
from tecplot.exception import *
from tecplot.tecutil.tecinterprocess import (_TecInterprocess, _TecUtil,
                                             find_file)
from tecplot.tecutil import _tecinterprocess, _tecutil, ArgList, lock
import platform

from test import patch_tecutil


class MockInterprocessCDLL:
    @property
    def Start(self):
        class StartObj(object):
            def __init__(self):
                self.restype = None
                self.argtypes = None

            def __call__(self, sdkhome):
                return 2
        return StartObj()

    def Stop(self):
        return None

    @property
    def LicenseInfo(self):
        class LicenseInfoObj(object):
            def __init__(self):
                self.restype = None

            def __call__(self):
                return ''
        return LicenseInfoObj()

    @property
    def GetTUAssertErrorMessage(self):
        class GetTUAssertErrorMessageObj(object):
            def __init__(self):
                self.restype = None

            def __call__(self):
                return ''

        return GetTUAssertErrorMessageObj()


class TestTecInterprocess(unittest.TestCase):

    def setUp(self):
        self.noexit = patch('sys.exit')
        self.noexit.start()

    def tearDown(self):
        self.noexit.stop()

    def test___init__(self):
        _tecinterprocess = _TecInterprocess()
        self.assertIsInstance(_tecinterprocess, _TecInterprocess)

    def test_pyqt_message(self):
        with patch('ctypes.cdll.LoadLibrary',
                   Mock(return_value=MockInterprocessCDLL())):
            with patch('logging.Logger.info') as log:
                sys.modules['PyQt4'] = None
                _tip = _TecInterprocess()
                del sys.modules['PyQt4']
                self.assertEqual(log.call_count, 2)
                self.assertRegex(str(log.call_args_list[0]), r'.*PyQt.*')

    def test_find_file(self):
        with NamedTemporaryFile() as ftmp:
            self.assertEqual(path.abspath(ftmp.name),
                             find_file([path.basename(ftmp.name)],
                                       [path.dirname(ftmp.name)]))

    def test_tecsdkhome(self):
        oldhome = os.environ.get('TECSDKHOME', None)

        with patch.object(_TecInterprocess, '__init__',
                          Mock(return_value=None)):
            tip = _TecInterprocess()
            tip.tecinterprocess_path = 'test/test/test'
        os.environ['TECSDKHOME'] = '/non/existant/path'
        self.assertEqual(tip.tecsdkhome, 'test')

        del tip._tecsdkhome
        tip.tecinterprocess_path = None
        self.assertEqual(tip.tecsdkhome, '')

        tip.tecsdkhome = 'test'
        self.assertEqual(tip.tecsdkhome, 'test')

        del tip._tecsdkhome
        # homeenv = 'HOMEPATH' if platform.system() == 'Windows' else 'HOME'
        if platform.system() == 'Windows':
            homedir = path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
        else:
            homedir = os.environ['HOME']
        os.environ['TECSDKHOME'] = homedir
        self.assertEqual(tip.tecsdkhome, homedir)

        if oldhome is None:
            del os.environ['TECSDKHOME']
        else:
            os.environ['TECSDKHOME'] = oldhome

    def test_not_64bit_python(self):
        with patch('ctypes.sizeof', Mock(return_value=0)):
            self.assertRaises(TecplotLibraryNotLoadedError, _TecInterprocess)

    def test_unknown_platform(self):
        with patch('platform.system', Mock(return_value='')):
            self.assertRaises(KeyError, _TecInterprocess)

    def test_other_known_platforms(self):
        if platform.system() == 'Windows':
            with patch('platform.system', Mock(side_effect=('Linux',
                                                            'Darwin'))):
                self.assertRaises(TecplotLibraryNotFoundError, _TecInterprocess)
                self.assertRaises(TecplotLibraryNotFoundError, _TecInterprocess)
        elif platform.system() == 'Linux':
            with patch('platform.system', Mock(side_effect=('Windows',))):
                self.assertRaises(TecplotLibraryNotFoundError, _TecInterprocess)
        elif platform.system() == 'Darwin':
            with patch('platform.system', Mock(side_effect=('Windows',))):
                self.assertRaises(TecplotLibraryNotFoundError, _TecInterprocess)

    def test_load_library_failure(self):
        with patch('ctypes.cdll.LoadLibrary', Mock(return_value=None)):
            self.assertRaises((TecplotLibraryNotFoundError,
                               TecplotLibraryNotLoadedError), _TecInterprocess)

    def test_load_failures(self):

        if platform.system() in ['Linux', 'Darwin']:
            libpathenv = 'DYLD_LIBRARY_PATH' \
                         if platform.system() == 'Darwin' \
                         else 'LD_LIBRARY_PATH'
            ldlibpath = os.environ.get(libpathenv, None)
            if ldlibpath is not None:
                del os.environ[libpathenv]

            # Test: load_linux._syslibpath
            with patch('ctypes.cdll.LoadLibrary', Mock(return_value=None)):
                with patch('tecplot.tecutil.tecinterprocess.Popen',
                           Mock(side_effect=Exception)):
                    self.assertRaises(TecplotLibraryNotFoundError,
                                      _TecInterprocess)

                class MockPopen(Mock):
                    def communicate(self):
                        out = b'/non/existant/path\n'
                        err = b'\n'
                        return out, err

                with patch('tecplot.tecutil.tecinterprocess.Popen',
                           MockPopen()):
                    self.assertRaises(TecplotLibraryNotFoundError,
                                      _TecInterprocess)

            def _findlib(libnames, libpath):
                if libpath is None:
                    return None
                for lib in libnames:
                    for d in libpath.split(os.pathsep):
                        fpath = os.path.join(d, lib)
                        if os.path.exists(fpath):
                            return fpath

            with patch('ctypes.cdll.LoadLibrary', Mock(side_effect=OSError)):
                self.assertRaises(TecplotLibraryNotFoundError, _TecInterprocess)

                foundlib = _findlib(['libtecinterprocess.so'], ldlibpath)
                if foundlib is not None:
                    os.environ[libpathenv] = os.path.dirname(foundlib)

                self.assertRaises(TecplotLibraryNotLoadedError,
                                  _TecInterprocess)

                envpath = os.environ.get('PATH', None)
                os.environ['PATH'] = '.'
                self.assertRaises(TecplotLibraryNotLoadedError,
                                  _TecInterprocess)
                if envpath is not None:
                    os.environ['PATH'] = envpath

            if ldlibpath is not None:
                os.environ[libpathenv] = ldlibpath

            with patch('ctypes.cdll.LoadLibrary',
                       Mock(side_effect=(None, Exception))):
                self.assertRaises(TecplotLibraryNotLoadedError,
                                  _TecInterprocess)

            # Test: load_linux._missinglibs
            with patch('ctypes.cdll.LoadLibrary', Mock(return_value=None)):
                with patch('tecplot.tecutil.tecinterprocess.Popen',
                           Mock(side_effect=Exception)):
                    self.assertRaises(TecplotLibraryNotLoadedError,
                                      _TecInterprocess)

            class MockPopen(Mock):
                def communicate(self):
                    out = b'    libexception.so => not found\n'
                    err = b'\n'
                    return out, err

            with patch('ctypes.cdll.LoadLibrary', Mock(return_value=None)):
                with patch('tecplot.tecutil.tecinterprocess.Popen',
                           MockPopen()):
                    self.assertRaises(TecplotLibraryNotLoadedError,
                                      _TecInterprocess)

    def test_start_stop(self):
        with patch('ctypes.cdll.LoadLibrary',
                   Mock(return_value=MockInterprocessCDLL())):
            _tip = _TecInterprocess()
            self.assertRaises(TecplotLicenseError, _tip.start)
            self.assertEqual(_tip.stop(), None)

            _tip.started = True
            with self.assertRaises(TecplotLibraryNotLoadedError):
                _tip.start()

        def fn(*a):
            raise Exception
        _tip.handle.Stop = fn

        _tip.stopped = True
        _tip.stop()
        _tip.stopped = False
        self.assertRaises(Exception, _tip.stop)

    def test_license_validation(self):
        with patch('ctypes.cdll.LoadLibrary',
                   Mock(return_value=MockInterprocessCDLL())):
            _tip = _TecInterprocess()

            with patch.object(_tip, 'start'):
                _tip.started = True
                _tip.handle.LicenseIsValid = lambda *a: True
                self.assertTrue(_tip.license_is_valid)

                _tip.handle.AcquireLicense = lambda *a: True
                _tip.acquire_license()

                _tip.handle.LicenseIsValid = lambda *a: False
                self.assertIsNone(_tip.acquire_license())
                self.assertFalse(_tip.license_is_valid)

                _tip.handle.AcquireLicense = lambda *a: False
                self.assertRaises(TecplotLicenseError, _tip.acquire_license)

                _tip.handle.ReleaseLicense = lambda *a: 1 / 0
                _tip.release_license()

                _tip.handle.LicenseIsValid = lambda *a: True
                self.assertRaises(Exception, _tip.release_license)

    def test_error(self):
        _tecinterprocess.clear_last_message()
        self.assertIsNone(_tecinterprocess.last_message)

        # trigger a TUAssert...
        _tecinterprocess.handle.tecUtilStateChangedX(None)

        # error is there and is a string message
        last_message = _tecinterprocess.update_last_message()
        self.assertIsInstance(last_message.message, string_types)
        self.assertIsInstance(_tecinterprocess.last_message.message,
                              string_types)

        _tecinterprocess.clear_last_message()
        self.assertIsNone(_tecinterprocess.last_message)

        with self.assertRaises(TecplotLogicError):
            _tecutil.StateChangedX(None)

        # message already updated
        self.assertIsNone(_tecinterprocess.update_last_message())
        self.assertIsInstance(_tecinterprocess.last_message.message,
                              string_types)
        _tecinterprocess.clear_last_message()

        # check that error is clear
        self.assertIsNone(_tecinterprocess.last_message)

    def test_log(self):
        with patch('ctypes.cdll.LoadLibrary',
                   Mock(return_value=MockInterprocessCDLL())):
            _tip = _TecInterprocess()
            with patch('logging.Logger.log') as log:
                cnt = log.call_count
                _tip._last_message = _TecInterprocess.Message(0, 'test')
                _tip.log_last_message()
                self.assertEqual(log.call_count, cnt + 1)

                _tip._last_message = _TecInterprocess.Message(0, '')
                _tip.log_last_message()
                self.assertEqual(log.call_count, cnt + 1)

                _tip._last_message = None
                _tip.log_last_message()
                self.assertEqual(log.call_count, cnt + 1)

    def test_last_error(self):
        with self.assertRaises(TecplotSystemError):
            tp.macro.execute_command('$!bad macro command')
        if __debug__:
            self.assertIsNotNone(_tecinterprocess.last_message)
        else:
            self.assertIsNone(_tecinterprocess.last_message)
        _tecinterprocess.clear_last_message()

    def test_no_sdk(self):
        tip = _tecinterprocess
        if hasattr(tip, '_sdk_version_info'):
            del tip._sdk_version_info
        with patch.object(tip.handle, 'tecUtilTecplotGetMajorVersion',
                          side_effect=AttributeError):
            self.assertIsInstance(tp.sdk_version_info,
                                  tp.tecutil.tecinterprocess.SDKVersion)
            self.assertEqual(tip.sdk_version, 'unknown')

        with patch('tecplot.tecutil.tecutil._TecUtil.__init__',
                   Mock(side_effect=AttributeError)):
            with self.assertRaises(TecplotInitializationError):
                tip.initialize_tecutil()

    def test_preamble(self):

        info = tp.tecutil.tecinterprocess._TecInterprocess.Message(logging.INFO, 'info')
        error = tp.tecutil.tecinterprocess._TecInterprocess.Message(logging.ERROR, 'error')

        with patch('ctypes.cdll.LoadLibrary',
                   Mock(return_value=MockInterprocessCDLL())):
            tecinter = 'tecplot.tecutil.tecinterprocess._TecInterprocess.'
            with patch(tecinter+'acquire_license',Mock(side_effect=Exception)):
                with patch(tecinter+'update_last_message', Mock(return_value=info)):
                    with patch(tecinter+'log_last_message', Mock()) as loglast:
                        with self.assertRaises(Exception):
                            _tecutil.LockGetCount()
                        self.assertEqual(loglast.call_count, 1)
                with patch(tecinter+'update_last_message', Mock(return_value=error)):
                    with self.assertRaises(TecplotLogicError):
                        _tecutil.LockGetCount()
            with patch(tecinter+'acquire_license',
                       Mock(side_effect=TecplotInitializationError)):
                with self.assertRaises(TecplotInitializationError):
                    _tecutil.LockGetCount()
            with patch(tecinter+'update_last_message', Mock(return_value=info)):
                with patch(tecinter+'log_last_message', Mock()) as loglast:
                    _tecutil.LockGetCount()
                    if __debug__:
                        self.assertEqual(loglast.call_count, 1)
                    else:
                        self.assertEqual(loglast.call_count, 0)
            with patch(tecinter+'update_last_message', Mock(return_value=error)):
                with self.assertRaises(TecplotLogicError):
                    _tecutil.LockGetCount()
            with patch(tecinter+'update_last_message', Mock(return_value=None)):
                _tecutil.LockGetCount()

    def test_license_expiration(self):
        tip = _tecinterprocess
        with patch.object(tip.handle, 'LicenseExpirationDate',
                          Mock(return_value=b'31-Dec-2020')):
            self.assertEqual(tip.license_expiration,
                             datetime.date(year=2020,month=12,day=31))
        with patch.object(tip.handle, 'LicenseExpirationDate',
                          Mock(return_value=b'permanent')):
            self.assertIsInstance(tip.license_expiration, string_types)

        try:
            expire_soon = datetime.date.today() + datetime.timedelta(days=5)
            expire_soon_bytes = expire_soon.strftime('%d-%b-%Y').encode()
            expire_later = datetime.date.today() + datetime.timedelta(days=180)
            expire_later_bytes = expire_later.strftime('%d-%b-%Y').encode()
            with patch.object(tip.handle, 'Start', Mock(return_value=0)):
                with patch.object(tip.handle, 'LicenseExpirationDate',
                        PropertyMock(return_value=expire_soon_bytes)):
                    with catch_warnings(record=True) as w:
                        tip.started = False
                        tip.start()
                        msg = str(w[-1].message)
                        self.assertRegex(msg, r'^((?!roaming).)*')
                        self.assertRegex(msg, r'TecPLUS')
                        self.assertRegex(msg, r'\*\*5 days\*\*')
                    with patch.object(tip.handle, 'LicenseIsRoaming',
                            PropertyMock(return_value=True)):
                        with catch_warnings(record=True) as w:
                            tip.started = False
                            tip.start()
                            msg = str(w[-1].message)
                            self.assertRegex(msg, r'roaming')
                            self.assertRegex(msg, r'^((?!TecPlus).)*')
                            self.assertRegex(msg, r'\*\*5 days\*\*')
                with patch.object(tip.handle, 'LicenseExpirationDate',
                        PropertyMock(return_value=expire_later_bytes)):
                    with catch_warnings(record=True) as w:
                        tip.started = False
                        tip.start()
                        self.assertEqual(len(w), 0)
        finally:
            tip.started = True

    def test_roaming(self):
        expire_date = datetime.date(year=2020,month=12,day=31)
        tip = _tecinterprocess
        tecinter = 'tecplot.tecutil.tecinterprocess._TecInterprocess.'
        with patch.object(tip, 'acquire_license'):
            with patch(tecinter+'license_expiration',
                       PropertyMock(return_value=expire_date)):
                with patch.object(tip.handle, 'LicenseStartRoaming',
                                  Mock(return_value=True)):
                    tip.start_roaming(5)
                    with patch(tecinter+'license_expiration',
                               PropertyMock(return_value='permanent')):
                        tip.start_roaming(5)
                with patch.object(tip.handle, 'LicenseStartRoaming',
                                  Mock(return_value=False)):
                    self.assertRaises(TecplotLicenseError,
                                      lambda: tip.start_roaming(5))
            with patch.object(tip.handle, 'LicenseStopRoaming',
                              Mock(return_value=True)):
                tip.stop_roaming()
            with patch.object(tip.handle, 'LicenseStopRoaming',
                              Mock(return_value=False)):
                self.assertRaises(TecplotLicenseError, tip.stop_roaming)


class TestTecutil(unittest.TestCase):

    def test___init__(self):
        _tecutil = _TecUtil(_tecinterprocess)
        self.assertIsInstance(_tecutil, _TecUtil)

    def test_exceptions(self):
        with self.assertRaises(TecplotLogicError):
            _tecutil.StateChangedX(None)  # ctypes OK, TUAsserts

        with self.assertRaises(TypeError):
            _tecutil.AnimateIJKPlanes(None)  # ctypes wrong nargs

        with self.assertRaises(AttributeError):
            _tecutil.FieldLayerIsActive(1)  # ctypes wrong arg type

if __name__ == '__main__':
    from .. import main
    main()
