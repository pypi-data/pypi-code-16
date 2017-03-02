"""
An example based off the MovieLens 20M dataset, found here
https://grouplens.org/datasets/movielens/

Since this dataset contains explicit 5-star ratings, the ratings are
filtered down to positive reviews (4+ stars).

"""

from __future__ import print_function

import argparse
import logging
import os
import time

import numpy
import pandas
from scipy.sparse import coo_matrix

from implicit.als import AlternatingLeastSquares
from implicit.nearest_neighbours import (BM25Recommender, CosineRecommender,
                                         TFIDFRecommender, bm25_weight)


def read_data(path, min_rating=5.0):
    """ TODO """
    ratings = pandas.read_csv(os.path.join(path, "ratings.csv"))
    positive = ratings[ratings.rating >= min_rating]

    movies = pandas.read_csv(os.path.join(path, "movies.csv"))

    m = coo_matrix((positive['rating'].astype(float), (positive['movieId'], positive['userId'])))
    m.data = numpy.ones(len(m.data))
    return ratings, movies, m


def calculate_similar_movies(input_path, output_filename,
                             model_name="als"):
    # read in the input data file
    logging.debug("reading data from %s", input_path)
    start = time.time()
    ratings, movies, m = read_data(input_path)
    logging.debug("read data file in %s", time.time() - start)

    # generate a recommender model based off the input params
    if model_name == "als":
        model = AlternatingLeastSquares()

        # lets weight these models by bm25weight.
        logging.debug("weighting matrix by bm25_weight")
        m = bm25_weight(m,  B=0.9) * 5

    elif model_name == "tfidf":
        model = TFIDFRecommender()

    elif model_name == "cosine":
        model = CosineRecommender()

    elif model_name == "bm25":
        model = BM25Recommender(B=0.2)

    else:
        raise NotImplementedError("TODO: model %s" % model_name)

    # train the model
    logging.debug("training model %s", model_name)
    start = time.time()
    model.fit(m)
    logging.debug("trained model '%s' in %s", model_name, time.time() - start)
    logging.debug("calculating top movies")

    user_count = ratings.groupby('movieId').size()
    movie_lookup = dict((i, m) for i, m in zip(movies['movieId'], movies['title']))
    to_generate = sorted(list(movies['movieId']), key=lambda x: -user_count.get(x, 0))

    with open(output_filename, "w") as o:
        for movieid in to_generate:
            movie = movie_lookup[movieid]
            for other, score in model.similar_items(movieid, 11):
                o.write("%s\t%s\t%s\n" % (movie, movie_lookup[other], score))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates related artists on the last.fm dataset",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--input', type=str,
                        dest='inputfile', help='last.fm dataset file', required=True)
    parser.add_argument('--output', type=str, default='similar-movies.tsv',
                        dest='outputfile', help='output file name')
    parser.add_argument('--model', type=str, default='als',
                        dest='model', help='model to calculate (als/bm25/tfidf/cosine)')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    calculate_similar_movies(args.inputfile, args.outputfile,
                             model_name=args.model)
