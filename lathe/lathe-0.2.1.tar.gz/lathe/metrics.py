from __future__ import division
import numpy as np


def _ensure_same_shape(predictions, targets):
    predictions = np.atleast_1d(predictions).flatten()
    targets = np.atleast_1d(targets).flatten()

    if predictions.shape != targets.shape:
        msg = "shape mismatch: cannot compare objects with different shapes"
        raise ValueError(msg)

    return predictions, targets


def mse(predictions, targets):
    # return sklearn.metrics.mean_squared_error(predictions, targets)
    return np.nanmean((predictions - targets)**2)
    # return np.sum((predictions - targets)**2)


def rmse(predictions, targets):
    return np.sqrt(mse(predictions, targets))


# TODO: figure out something better than not using exact
def measure_error(predictions, targets, rtol=0, evaluator=mse):
    predictions, targets = _ensure_same_shape(predictions, targets)
    return evaluator(predictions, targets)


def measure_accuracy(predictions, targets, rtol=0):
    p, t = _ensure_same_shape(predictions, targets)
    idx = np.isclose(p, t, rtol=rtol) if rtol else p == t
    return np.minimum(1.0, np.count_nonzero(idx) / len(targets))


def evaluate(data,
             targets,
             predict_function,
             measure_functions=None,
             rtol=0,
             progress=False,
             *args):
    if not measure_functions:
        measure_functions = [measure_error, measure_accuracy]

    it = data
    if progress:
        try:
            import tqdm
            it = tqdm.tqdm(data)
        except ImportError:
            print("install tqdm to display progress")

    predictions = []
    for instance in it:
        predictions.append(predict_function(instance, *args))

    return (fn(predictions, targets, rtol=rtol) for fn in measure_functions)
