import os
import subprocess
import time
from pySMS.utils.excepetions import NetworkDriveError, NetworkError
from pySMS.pgsql.postgres import Postgres

DEFAULT_REMOTE_SHARE_NAME = r"\\nam\wardfs"
DEFAULT_DRIVE_LETTER = "G:"
DEFAULT_PROGRAM_LOCATION = r"G:\Dist\Centralized Inventory\ZB - Loaners Department\Ian"
VPN_HOST_IP_ADDRESS = "12.40.148.10"
POSTGRES_ADDRESS = "vsbslgprd01.zmr.zimmer.com"


class Protocols:

    def __init__(self):
        self.pg = Postgres()

    def test_connection(self, retry=5, address=POSTGRES_ADDRESS):
        for _ in range(retry):
            try:
                self.pg.test_connection(connection="MANUAL", username="doarni", password="ZimmerBiomet", host=address, verbose=False)
                return
            except:
                if _ < retry:
                    print('No connection established, retrying connection [' + str(_) + ']')
                    continue
                elif _ >= retry:
                    raise NetworkError("Please check to see if you are connected to the internet via VPN",
                                       issue="ServerConnectionFailed",
                                       msg="Connection to the server failed")

    @staticmethod
    def protocol_data():
        return {"DEFAULT_REMOTE_SHARE_NAME": DEFAULT_REMOTE_SHARE_NAME,
                "DEFAULT_DRIVE_LETTER": DEFAULT_DRIVE_LETTER,
                "DEFAULT_PROGRAM_LOCATION": DEFAULT_PROGRAM_LOCATION,
                "VPN_HOST_IP_ADDRESS": VPN_HOST_IP_ADDRESS,
                "POSTGRES_ADDRESS": POSTGRES_ADDRESS}


class NetworkDrive:

    def __init__(self):
        p = Protocols()
        p.test_connection()

        self.protocol_data = p.protocol_data()
        self.network_drive_path = self.check_for_map()


    def map_shared_drive(self, location=DEFAULT_REMOTE_SHARE_NAME, drive=DEFAULT_DRIVE_LETTER, retry=5, sleep=1):
        iter = 0
        for _ in range(retry  + 1):
            if not _ >= retry:
                try:
                    subprocess.check_call(["net", "use", drive, location])
                    print('Connection to network drive [' + location + '] established [' + drive + '].')
                    return {'return': 1, 'msg': 'successful_map'}
                except Exception as e:
                    iter += 1
                    time.sleep(sleep)
                    print('Mapping failed. Attempting re-map [' + str(_ + 1) + '] of [' + str(retry) + ']')
                    continue
            elif _ >= retry:
                raise NetworkDriveError(location + ' Could not be to map to ' + drive + ' after [' + str(iter) + '] retrys', issue="MappingFailed")

    def check_for_map(self):
        if os.path.exists(DEFAULT_PROGRAM_LOCATION) == True:
            print('Connection to network drive [' + DEFAULT_REMOTE_SHARE_NAME + '] established [' + DEFAULT_DRIVE_LETTER + '].')
            return DEFAULT_PROGRAM_LOCATION
        else:
            try:
                self.map_shared_drive()
            except:
                raise NetworkDriveError('Please check to see if the drive is mapped correctly and that you are connected to a ZimmerBiomet VPN / Internet.',issue='DriveNotFound', msg=None)

    def set_current_dir(self, _dir_):
        if not _dir_.__contains__(r'C:'):
            os.chdir(self.network_drive_path + _dir_)
            return os.getcwd()
        else:
            raise NetworkDriveError('Incorrect volume label. You must stay in the G:\ drive.', issue='IncorrectVolumeError')

    def clean_core_version(self, verbose=False):
        _path = self.set_current_dir(r"\SMSA\Python\program\core")
        fs = [f for f in os.listdir(_path) if f.endswith('')]

        for file in fs:
            if verbose != False:
                print('Removing [{}] from [{}]'.format(file, DEFAULT_DRIVE_LETTER + DEFAULT_REMOTE_SHARE_NAME))
                os.system("""del /s /q {}""".format(file))
            else:
                os.system("""del /s /q {}""".format(file))


    def get_files_from_directory(self, directory, abs_path=False, file_types=[], ignore=[]):
        _path = self.set_current_dir(directory)
        _files = [f for f in os.listdir(_path) if f.endswith('')]
        return_list = []
        if len(file_types) == 0:
            raise NetworkDriveError('No file types provided for file search', issue="NoFilesSpecified")
        else:
            for f in _files:
                if len(ignore) == 0:
                    if abs_path != False:
                        return_list.append(_path + '\\' + f)
                    else:
                        return_list.append(f)
                else:
                    ext = f.split('.')[1]
                    if ext not in ignore:
                        if abs_path != False:
                            return_list.append(_path + '\\' + f)
                        else:
                            return_list.append(f)
            return return_list
