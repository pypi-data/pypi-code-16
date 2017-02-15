from addok.config.default import PROCESSORS
from addok.config.local import *  # noqa

RESULTS_COLLECTORS = [
    'addok.helpers.collectors.only_commons',
    'addok.helpers.collectors.bucket_with_meaningful',
    'addok.helpers.collectors.reduce_with_other_commons',
    'addok.helpers.collectors.ensure_geohash_results_are_included_if_center_is_given',  # noqa
    'addok_trigrams.extend_results_removing_numbers',
    'addok_trigrams.extend_results_removing_one_whole_word',
    'addok_trigrams.extend_results_removing_successive_trigrams',
]
PROCESSORS = PROCESSORS + [
    'addok_trigrams.trigramize',
]
SEARCH_RESULT_PROCESSORS = [
    'addok_trigrams.match_housenumber',
    "addok_france.make_labels",
    'addok.helpers.results.score_by_importance',
    'addok.helpers.results.score_by_autocomplete_distance',
    'addok.helpers.results.score_by_ngram_distance',
    'addok.helpers.results.score_by_geo_distance',
]
REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 2
}
