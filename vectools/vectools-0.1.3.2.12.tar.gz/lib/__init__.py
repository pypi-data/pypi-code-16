# This file controls which input names call which functions.

from lib import normalization, mathematics, manipulation, analysis, descriptor_CLI_interfaces, supervised_learning, \
    unsupervised_learning, graph

__version__ = '0.1'

__all__ = [
    "normalization",
    "mathematics",
    "manipulation",
    "analysis",
    "descriptor_CLI_interfaces",
    "supervised_learning",
    "unsupervised_learning",
    "graph",
]

operations_dict = {
    "Normalization": {
        "zscorenorm": normalization.z_score_normalization,
        "quantnorm":  normalization.quantile_normalization,
        "medpolish":  normalization.median_polish_normalization
    },
    "Math": {
        "add": mathematics.add,
        "subtract": mathematics.subtract,
        "multiply": mathematics.multiply,
        "dotproduct": mathematics.dot_product,
        "inverse": mathematics.inverse,
        "determinant": mathematics.determinant,
        "eigenvec": mathematics.eigen_vectors,
        "eigenvalues": mathematics.eigen_values,
        "sum": mathematics.sum_up
    },
    "Manipulation": {
        "append":       manipulation.append_values_to,
        "aggregate":    manipulation.aggregate,
        "creatematrix": manipulation.create_matrix,
        "format":       manipulation.format_vec,
        "chop":         manipulation.chop,
        "concat":       manipulation.concatenate,
        "join":         manipulation.join,
        "vrep":         manipulation.vrep,
        "slice":        manipulation.vec_slice,
        "sort":         manipulation.vector_sort,
        "transpose":    manipulation.transpose,
        "unique":       manipulation.unique
        # "to_svmlight": manipulation.to_svmlight,
        # "svml_to_csv": manipulation.to_csv,
        # "makeaddable": makeaddable,
        # "append_matrix": append_matrix,
        # "max": colmax,
    },
    "Analysis and Statistics": {
        "runLDA": analysis.run_lda,
        "min": analysis.minimum,
        "max": analysis.maximum,
        "median": analysis.median,
        "sd": analysis.sd,
        "mean": analysis.average,
        "percentile": analysis.percentile,
        "pearson": analysis.pearson_group,
        "pca": analysis.run_pca,
        "shape": analysis.shape,
        "spearman": analysis.spearman,
        "confmat": analysis.confusion_matrix,
        "roc": analysis.roc_curve
    },
    "Descriptors": {
        "ncomp":       descriptor_CLI_interfaces.ncomposition_command_line,
        "splitncomp":  descriptor_CLI_interfaces.split_ncomposition_command_line,
        "physchem":    descriptor_CLI_interfaces.physicochemical_properties_ncomposition_command_line,
        "geary":       descriptor_CLI_interfaces.geary_autocorrelation_command_line,
        "mbroto":      descriptor_CLI_interfaces.normalized_moreaubroto_autocorrelation_command_line,
        "moran":       descriptor_CLI_interfaces.moran_autocorrelation_command_line,
        "pseudoaac":   descriptor_CLI_interfaces.pseudo_amino_acid_composition_command_line,
        "seqordcoup":  descriptor_CLI_interfaces.sequence_order_coupling_number_total_command_line,
        "quasiseqord": descriptor_CLI_interfaces.quasi_sequence_order_command_line,
        "summary":     analysis.summary
    },
    "Supervised Learning": {
        "svmtrain":    supervised_learning.svm_train,
        "svmclassify": supervised_learning.svm_classify,
        "linreg":      supervised_learning.linear_regression,
        "neuralnet":   supervised_learning.neural_network,
        "randforest":  supervised_learning.random_forest
    },
    "Unsupervised Learning": {
        "kmeans": unsupervised_learning.k_means_clustering,
        "dbscan": unsupervised_learning.DBSCAN,
        "affcl":  unsupervised_learning.affinity_propagation_clustering,
        "silscore": unsupervised_learning.silhouette_score,
    },
    "Graph Operations": {
        "edges":       graph.listedges,
        "addedge":     graph.addedge,
        "addnode":     graph.addnode,
        "paths":       graph.listpaths,
        "graphformat": graph.graphformat,
    }
}
