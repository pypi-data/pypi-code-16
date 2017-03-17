"""
Sweet docstring here.

"""
__version__ = "0.0.1"

import shutil


def arc_pack(target_path: str, archive_path: str, format='bztar') -> bool:
    """
    Compress directory at directory_path to archive at archive_path.

    :param target_path: Path to the directory to compress/archive.
    :param archive_path: Path to the created archive.
    :param compression_format: The compression format to use.
    :return: True if successful else False.
    """

    try:
        shutil.make_archive(base_name=archive_path,
                            root_dir=target_path,
                            format=format)
        resp = True
    except Exception as e:
        print(e)
        resp = False
    finally:
        return resp if resp else False


def arc_unpack(target_path: str,
               extract_dir: str = None,
               format: str = None) -> bool:
    """
    Extract archive at archive_path to extracted_path.

    :param target_path: Path to the archive to extract.
    :param extract_dir: Path to the extracted archive.
    :param format: Format of archive to extract
    :return: True if successful else False.
    """

    try:
        shutil.unpack_archive(filename=target_path,
                              extract_dir=extract_dir,
                              format=format)
        resp = True
    except Exception as e:
        print(e)
        resp = False
    finally:
        return resp
