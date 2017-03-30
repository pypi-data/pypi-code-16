import re
import arff
import numpy as np
import sklearn.model_selection
import sklearn.preprocessing


def shuffle(features, labels):
    if features.shape[0] != labels.shape[0]:
        raise ValueError(
            "Features {} and labels {} must have the same number of rows".
            format(features.shape, labels.shape))
    permutation = np.random.permutation(features.shape[0])
    return features[permutation], labels[permutation]


def k_fold(data, n_splits, shuffle=False):
    return sklearn.model_selection.KFold(n_splits, shuffle=shuffle).split(data)


def _split(data, label_size):
    return data[:, :-label_size], data[:, -label_size:]


# def split(data, percent_chunks, axis=0):
#     if data.ndim != 2:
#         raise ValueError("data to split must be a 2D numpy array")
#     splits = np.cumsum(percent_chunks)
#     if splits[-1] == 100:
#         splits = np.divide(splits, 100.)
#     if splits[-1] != 1.:
#         raise ValueError("Percents must sum to 1.0 or 100")
#     # np.random.shuffle(data)
#     return np.split(data, splits[:-1] * data.shape[1], axis)


def split(features, labels, percent):
    percent = float(percent)
    if not 0 < percent < 1:
        raise ValueError("percent must be in range: 0-1")
    index = int(percent * features.shape[0])
    return features[:index], features[index:], labels[:index], labels[index:]


# HACK: arff.load only accepts an open file descriptor
# and BYU CS uses a custom arff format
def _fix_attribute_types(f):
    # TODO: do not load entire contents of file into RAM at once
    f.seek(0)
    s = f.read()
    f.seek(0)
    s = re.sub(r'continuous', 'real', s, flags=re.IGNORECASE)
    f.write(s)
    f.truncate()
    f.seek(0)


def _find_nominal_index(data):
    return [
        i for i, (_, kind) in enumerate(data)
        if kind not in ['REAL', 'INTEGER', 'NUMERIC', 'STRING']
    ]


def _one_hot(data, index):
    encoder = sklearn.preprocessing.OneHotEncoder(
        categorical_features=index, sparse=False, handle_unknown='ignore')
    # TODO: How to not screw up the index? Use encoder.feature_indices_?
    return encoder.fit_transform(data)


def load(file_path,
         label_size=0,
         encode_nominal=True,
         one_hot_data=None,
         one_hot_targets=False,
         imputer=None,
         normalizer=None,
         shuffle=False):
    """Load an ARFF file.

    Args:
        file_path (str): The path of the ARFF formatted file to load.
        label_size (int, optional): The number of labels (outputs) the dataset
            to load has.
        encode_nominal (bool, optional): Whether or not to encode nominal
            atributes as integers.
        one_hot_data (bool, optional): Whether or not to use a one-hot encoder
            for nominal attributes in `data`. Defaults to whatever the value of
            `encode_nominal` is.
        one_hot_targets (bool, optional): Whether or not to use a one-hot
            encoder for nominal attributes in `targets`.
        imputer (function, optional): A 1 arity function that accepts the
            dataset to impute missing values over.
            e.g: `sklearn.preprocessing.Imputer().fit_transform`.
            Defaults to `None`.
        normalizer (function, optional): A 1 arity function that accepts the
            data to be scaled as a parameter and returns the scaled data.
            e.g: `sklearn.preprocessing.scale`. Defaults to `None`.
        shuffle (bool, optional): Whether or not to shuffle the `data`.

    Returns:
        (list, `numpy.ndarray`, `numpy.ndarray`): Tuple containing
        (`attributes`, `data`, `targets`). Where `attributes` is a list of
        tuples containing (attribute_name, attribute_type), `data` are the
        features and `targets` are the expected output for the dataset.

    Note:
        `targets` will be empty unless `label_size` >= 1.

    See Also:
        - http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html
        - http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.Imputer.html
        - http://www.cs.waikato.ac.nz/ml/weka/arff.html
    """
    if one_hot_data is None:
        one_hot_data = encode_nominal

    with open(file_path, 'r+') as f:
        try:
            arff_data = arff.load(f, encode_nominal=encode_nominal)
        except arff.BadAttributeType:
            _fix_attribute_types(f)
            arff_data = arff.load(f, encode_nominal=encode_nominal)

    data = np.array(arff_data['data'], dtype=np.float)

    if imputer:
        data = imputer(data)

    if shuffle:
        np.random.shuffle(data)

    data, targets = _split(data, label_size)

    # have to do this twice because sklearn screws with the indices
    if one_hot_data:
        data_idx = _find_nominal_index(arff_data['attributes'][:-label_size])
        data = _one_hot(data, data_idx)
    if one_hot_targets:
        target_idx = _find_nominal_index(arff_data['attributes'][-label_size:])
        targets = _one_hot(targets, target_idx)

    if normalizer:
        data = normalizer(data)

    return arff_data['attributes'], data, targets
