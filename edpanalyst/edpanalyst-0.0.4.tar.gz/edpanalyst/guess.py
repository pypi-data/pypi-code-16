import collections
import six

import numpy as np  # type: ignore
import scipy.stats  # type: ignore

from .population_schema import PopulationSchema, ColumnDefinition


def guess_schema(df):  # type (...) -> PopulationSchema
    """Guesses a schema for a data frame."""
    coldefs = {col: _guess_given_vals(col, df[col])
               for col in df.columns}
    return PopulationSchema(coldefs, order=df.columns)


# How small a number of values guarantees categorical
_CATEGORICAL_THRESHOLD = 20

# How many values should cover what fraction of the space to accept
# categorical?
_CATEGORICAL_COVERAGE_COUNT = 10
_CATEGORICAL_COVERAGE_RATIO = 0.6


def _guess_given_vals(col_name, data):
    """Returns a guess as to the definition of a column given its data.

    The guess is in the form of a column definition like those in an EDP
    population schema.

    These heuristics are utterly unprincipled and simply seem to work well
    on a minimal set of test datasets. They should be treated fluidly and
    improved as failures crop up.
    """
    total_count = len(data)
    non_null = len(data.dropna())
    vals = data.unique()
    cardinality = len(data.dropna().unique())
    nonnum_vals = [v for v in vals if not _numbery(v)]
    nonnum = len(nonnum_vals)
    counts = data.dropna().value_counts()
    if non_null:
        coverage = (counts.iloc[:_CATEGORICAL_COVERAGE_COUNT].sum()
                    * 1.0 / non_null)

    # Constant columns are uninteresting. Do not model them.
    if cardinality == 0:
        return _col_def(col_name, 'void', 'Column is empty')
    if cardinality == 1:
        return _col_def(col_name, 'void', 'Column is constant')
    # Use cardinality for anything with less than 20 values, even numbers.
    elif cardinality < 20:
        return _col_def(
            col_name,
            'categorical',
            'Only %d distinct values' % cardinality,
            categorical_values=infer_categorical_values(data))
    elif nonnum == 0:
        # We have to do math. Turn them into the numbers they are.
        converted_vals = np.array([float(v) for v in vals])
        stat_type = _most_likely_numeric_distribution(converted_vals)
        return _col_def(
            col_name, stat_type,
            'Contains exclusively numbers (%d of them)' % (len(vals)))
    elif cardinality == total_count:
        return _col_def(col_name, 'void', 'Non-numeric and all values unique')
    elif coverage > _CATEGORICAL_COVERAGE_RATIO:
        reason = ('{} distinct values, {} non-numeric,' +
                  ' first {} cover {:.2%} of the space').format(
                  cardinality, nonnum, _CATEGORICAL_COVERAGE_COUNT,
                  coverage)
        return _col_def(
            col_name,
            'categorical',
            reason,
            categorical_values=infer_categorical_values(data))
    else:
        # Ignore anything with more than 20 distinct non-numeric values
        # and poor coverage.
        nonnum_str = ", ".join(nonnum_vals[:3])
        if nonnum > 3:
            nonnum_str += ", ..."
        return _col_def(col_name, 'void', '%d distinct values. '
                        '%d are non-numeric (%s)' %
                        (cardinality, nonnum, nonnum_str))


def infer_categorical_values(data):
    # TODO(asilvers): Categoricals have to be strings, but auto-converting
    # still allows ambiguity in representations of floats. This probably
    # doesn't get solved until guess is done on the server.
    str_vals = data.dropna().unique().astype(six.text_type)
    # TODO(asilvers): What order do we want to use here? Lexicographic?
    # Descending frequency? This is also the order that gets used in UIs
    # (should that stay true?) so getting it right-ish for humans is also
    # important. Currently this is just lexicographic except with a silly hack
    # to sort numbers numerically and put them first.
    # Why zfill(10)? asilvers made up the 10. He figures if your numbers are
    # longer than that then are you really worried about if they're sorted?
    return sorted(str_vals, key=lambda v: v.zfill(10) if _numbery(v) else v)


def _col_def(name, stat_type, reason, categorical_values=None):
    return ColumnDefinition(name, stat_type, reason, values=categorical_values)


def _most_likely_numeric_distribution(vals):
    # TODO(asilvers): This has only been very lightly thought through.
    # It's not clear that directly comparing the log-likelihoods is correct,
    # nor is it clear that we want to assume a uniform prior across
    # these distributions. Also lots of other things are unclear. But it's
    # "guess", not "find me the absolute truth" so it'll do for now.

    # We're deliberately evaluating functions outside of their domain, e.g.
    # log of negative numbers. Suppress warnings while doing so.
    with np.errstate(divide='ignore', invalid='ignore'):
        likelihoods = [(_ml_norm_loglik(vals, _identity), 'realAdditive'),
                       (_ml_norm_loglik(vals, _log), 'realMultiplicative'),
                       (_ml_norm_loglik(vals, _logit), 'proportion')]
    most_likely = max(likelihoods, key=lambda x: x[0])
    return most_likely[1]


# Stores transformed data, as well as the (log) of the jacobian of the
# transformation. After mapping x to y=f(x), log_jacobian is log(df(x)/dx) as a
# function of y.
Transformed = collections.namedtuple('Transformed',
                                     ['data', 'log_jacobian'])


def _identity(vals):
    """The identity link function."""
    return Transformed(vals, np.zeros(len(vals)))


def _log(vals):
    """The log link function."""
    # TODO(asilvers): Dealing with negative numbers is weird.
    # How it works now:
    # np.log returns NaN for negative values which causes NaNs to propagate
    # throughout these calculations, making the final likelihood comparison
    # false if anything returned NaN. It's kind of icky.  One possibility is to
    # just not check log-normals at all if there are any negative numbers.
    # Another is to see if there's only one or two out of thousands of rows and
    # do something smart. But maybe that's for `suggest` and data cleaning, not
    # guess.
    logged_vals = np.log(vals)
    log_jacobian = -1 * logged_vals
    return Transformed(logged_vals, log_jacobian)


def _logit(vals):
    """The logit link function."""
    # TODO(asilvers): Same comments about handling negative numbers, except
    # this time about numbers outside the domain of logit.
    logited_vals = scipy.special.logit(vals)
    log_jacobian = -1 * np.log(vals) - np.log1p(-1 * vals)
    return Transformed(logited_vals, log_jacobian)


def _ml_norm_loglik(vals, link_function=_identity):
    """Returns the log-likelihood of `vals` under the most likely normal
    distribution, after transforming `vals` with `link_function`."""
    transformed_vals, jacobian = link_function(vals)
    mean, stddev = np.mean(transformed_vals), np.std(transformed_vals)
    lp = sum(scipy.stats.norm.logpdf(transformed_vals, mean, stddev))
    return lp + sum(jacobian)


def _numbery(val):
    "Returns True if a value looks like a number."""
    try:
        float(val)
        return True
    except ValueError:
        return False
    except TypeError:
        return False
