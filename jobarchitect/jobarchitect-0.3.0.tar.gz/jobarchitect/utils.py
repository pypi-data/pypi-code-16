"""Utilities for jobarchitect."""

import os
import errno

from dtool import DataSet


def mkdir_parents(path):
    """Create the given directory path.

    This includes all necessary parent directories. Does not raise an error if
    the directory already exists.

    :param path: path to create
    """

    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def path_from_hash(dataset_path, hash_str):
    """Return absolute path from a dataset given a hash.

    :param dataset_path: path to input dataset
    :param hash_str: dataset item identifier as a hash string
    :returns: absolute path to dataset item
    """
    dataset_path = os.path.abspath(dataset_path)
    dataset = DataSet.from_path(dataset_path)
    data_path = os.path.join(dataset_path, dataset.data_directory)
    for item in dataset.manifest["file_list"]:
        if item["hash"] == hash_str:
            return os.path.join(data_path, item["path"])
    raise(KeyError("File hash not in dataset"))


def split_dataset(dataset_path, nchunks):
    """Return generator yielding lists of file entries.

    :param dataset_path: path to input dataset
    :param nchunks: number of chunks the dataset items should be split into
    :returns: generator yielding lists of file entries
    """
    dataset_path = os.path.abspath(dataset_path)
    dataset = DataSet.from_path(dataset_path)

    file_list = dataset.manifest["file_list"]
    num_files = len(file_list)
    chunk_size = num_files // nchunks
    left_over_files = num_files % nchunks
    index = 0
    for n in range(nchunks, 0, -1):
        chunk = []
        for i in range(chunk_size):
            chunk.append(file_list[index])
            index += 1
        if n <= left_over_files:
            chunk.append(file_list[index])
            index += 1
        yield chunk


def output_path_from_hash(dataset_path, hash_str, output_root):
    """Return absolute output path for a dataset item.

    A.k.a. the absolute path to which output data should be written for the
    datum specified by the given hash.

    This function is not responsible for creating the directory.

    :param dataset_path: path to input dataset
    :param hash_str: dataset item identifier as a hash string
    :param output_root: path to output root
    :raises: KeyError if hash string identifier is not in the dataset
    :returns: absolute output path for a dataset item specified by the
              identifier
    """

    dataset_path = os.path.abspath(dataset_path)
    dataset = DataSet.from_path(dataset_path)

    for item in dataset.manifest["file_list"]:
        if item["hash"] == hash_str:
            return os.path.join(output_root, item["path"])
    raise(KeyError("File hash not in dataset"))
