"""
This module contains functions related to unsupervised learning.
"""
import sys
import numpy as np
from lib.inputoutput import ParseVectors, _shared_params, _slice_list
from select import select


def kmeans(parser):
    """ Preforms k-means clustering on a set of vectors.

    :param parser:
    :return:
    """

    from sklearn.cluster import KMeans

    parser.add_argument(
        'infile',
        nargs='?',
        type=str,
        default="sys.stdin"
    )

    parser.add_argument(
        '-v', "--print-input-vectors",
        action="store_true",
        help='Print the vectors after their class assignments.'
    )

    parser.add_argument(
        '-k',
        required=True,
        type=int,
        help=''
    )

    parser.add_argument(
        '-rs', '--random-state',
        type=int,
        default=None,
        help=''
    )

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    # Parse the vectors
    vector_parser = ParseVectors(
        file_name=args.infile,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )
    vectors = vector_parser.parse()

    # Predict cluster memberships.
    y_pred = KMeans(n_clusters=args.k, random_state=args.random_state).fit_predict(vectors)  #

    #
    labled_vectors = []
    for i in range(len(vectors)):
        labled_vectors.append(np.insert(vectors[i], 0, y_pred[i]))

    ParseVectors("").out(
        labled_vectors,
        column_titles=vector_parser.col_titles,
        row_titles=vector_parser.row_titles
    )


def silhouette_score(parser):
    """ Calculate the silhouette score of a set of clusters.

    Input all as one vector
    OR
    as a label vector and main vector

    :param parser:
    :return:
    """
    from sklearn.metrics import silhouette_score

    # metrics.silhouette_score
    #parser.add_argument(
    #    'infile',
    #    nargs='?',
    #    type=str,
    #    default="sys.stdin"
    #)

    parser.add_argument(
        '--labels',
        type=str,
        help="The labels assigning vectors to classes.",
        default=None
    )

    parser.add_argument(
        '--vectors',
        type=str,
        help="Vectors that have been assigned to classes.",
        default=None
    )

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    lable_parser = ParseVectors(
        file_name=args.labels,
        has_col_names=False,  #  args.column_titles,
        has_row_names=False,  #  args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )
    labels = lable_parser.parse()
    labels = np.array([x[0] for x in labels])

    vector_parser = ParseVectors(
        file_name=args.vectors,
        has_col_names=False,  #  args.column_titles,
        has_row_names=False,  #  args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )
    vectors = vector_parser.parse()

    sil_score_obj = silhouette_score(
        vectors,
        labels,
        metric='euclidean',
        # sample_size=sample_size
    )

    print(sil_score_obj)


def som():
    # TODO
    x = 0


def heirarchical_cluster():
    # TODO
    x = 0
    # http://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering
    # http://scikit-learn.org/stable/auto_examples/cluster/plot_ward_structured_vs_unstructured.html
    # ward = AgglomerativeClustering(n_clusters=6, linkage='ward').fit(X)
    # ward = AgglomerativeClustering(n_clusters=6, connectivity=connectivity, linkage='ward').fit(X)
    pass


def DBSCAN(parser):
    """ Preforms density based clustering of a set of vectors.
    :param parser:
    :return:
    """

    from sklearn.cluster import DBSCAN

    parser.add_argument('matrices',
                        nargs='*',
                        help='Matrices to add to a base matrix.')

    parser.add_argument('--omit',
                        action="store_true",
                        help="Only print points landing within clusters.")

    parser.add_argument('--epsilon',
                        type=float,
                        default=0.5,
                        nargs=1,
                        help='Maximum distance between two samples to be labeled as in the same neighborhood.')

    parser.add_argument('--min-samples',
                        type=int,
                        default=5,
                        nargs=1,
                        help='Minimum number of samples needed for a neighborhood to be considered as a core point.')

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    sources = args.matrices
    # If a matrix is passed from stdin use this as the base matrix and add other to it.
    # Use the technique below to prevent hanging if no stdin info present.
    # https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/
    while sys.stdin in select([sys.stdin], [], [], 0)[0]:
        if sys.stdin.readable():
            sources.insert(0, "sys.stdin")
        break

    # assert sources != []

    # Use out matrix to print results, this is important for keeping track of if column names have been printed.
    out_matrix = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    row_titles, vectors = [], []
    for matrix_file_name in sources:
        mp = ParseVectors(
            matrix_file_name,
            has_col_names=args.column_titles,
            has_row_names=args.row_titles,
            delimiter=args.delimiter,
            only_apply_on_columns=args.only_apply_on
        )

        for row_title, vector in mp.generate():

            # Capture column titles of first matrix.
            # This might get automatically fixed in the future.
            if not out_matrix.col_titles:
                out_matrix.setcolumntitles(mp.getcolumntitles())

            row_titles.append(row_title)
            vectors.append(vector)

    # X = StandardScaler().fit_transform(X)
    db = DBSCAN(eps=args.epsilon, min_samples=args.min_samples).fit(vectors)

    for i in range(len(vectors)):
        if (args.omit and db.labels_[i] != -1) or (not args.omit):
            out_matrix.iterative_out(row_titles[i], np.append(db.labels_[i], vectors[i]), column_titles=None)

