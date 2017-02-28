

def operationselector(function_name):
    # "normalization"
    #if function_name == "ncomp":
    operation_function = None
    if function_name == "zscorenorm":
        from lib.normalization import zscorenorm as operation_function
    elif function_name == "quantilenorm":
        from lib.normalization import quantilenorm as operation_function
    elif function_name == "medianpolish":
        from lib.normalization import medianpolish as operation_function
    # Math
    elif function_name == "add":
        from lib.mathematics import add as operation_function
    elif function_name == "subtract":
        from lib.mathematics import subtract as operation_function
    elif function_name == "add_scalar":
        from lib.mathematics import addscalar as operation_function
    elif function_name == "multiply_scalar":
        from lib.mathematics import multiplyscalar as operation_function
    elif function_name == "multiply":
        from lib.mathematics import multiply as operation_function
    elif function_name == "dot_product":
        from lib.mathematics import dotproduct as operation_function
    elif function_name == "inverse":
        from lib.mathematics import inverse as operation_function
    elif function_name == "determinant":
        from lib.mathematics import determinant as operation_function
    elif function_name == "eigenvectors":
        from lib.mathematics import eigenvectors as operation_function
    elif function_name == "eigenvalues":
        from lib.mathematics import eigenvalues as operation_function
    elif function_name == "sum":
        from lib.mathematics import sumup as operation_function
    # Manipulation
    elif function_name == "append_values_to":
        from lib.manipulation import append_values_to as operation_function
    elif function_name == "to_svmlight":
        from lib.manipulation import to_svmlight as operation_function
    elif function_name == "svmlight_to_csv":
        from lib.manipulation import to_csv as operation_function
    elif function_name == "chop":
        from lib.manipulation import chop as operation_function
    elif function_name == "concatenate":
        from lib.manipulation import concatenate as operation_function
    #elif function_name ==  # "creatematrix": creatematrix,
    #elif function_name ==  # "makeaddable": makeaddable,
    elif function_name == "join":
        from lib.manipulation import join as operation_function
    elif function_name == "setgrep":
        from lib.manipulation import setgrep as operation_function
    elif function_name == "slice":
        from lib.manipulation import vec_slice as operation_function
    elif function_name == "sort":
        from lib.manipulation import vecsort as operation_function
    elif function_name == "transpose":
        from lib.manipulation import transpose as operation_function
    elif function_name == "unique":
        from lib.manipulation import unique as operation_function
    #elif function_name ==  # "append_matrix": append_matrix,
    #elif function_name ==  # "max": colmax,
    # Analysis and_Stats
    # "columnstats": columnstats,
    # "runLDA": runLDA,
    # "pearson": pearson,
    elif function_name == "min":
        from lib.analysis import minimum as operation_function
    elif function_name == "max":
        from lib.analysis import maximum as operation_function
    elif function_name == "median":
        from lib.analysis import median as operation_function
    elif function_name == "sd":
        from lib.analysis import sd as operation_function
    elif function_name == "mean":
        from lib.analysis import average as operation_function
    elif function_name == "percentile":
        from lib.analysis import percentile as operation_function
    elif function_name == "pearson":
        from lib.analysis import pearson_group as operation_function
    elif function_name == "pca":
        from lib.analysis import run_pca as operation_function
    elif function_name == "spearman":
        from lib.analysis import spearman as operation_function
    # "Descriptors"
    elif function_name == "ncomp": 
        from lib.descriptor_CLI_interfaces import ncompositioncommandline as operation_function
    elif function_name == "splitncomp": 
        from lib.descriptor_CLI_interfaces import splitncompositioncommandline as operation_function
    elif function_name == "physchem": 
        from lib.descriptor_CLI_interfaces import physicochemicalpropertiesncompositioncommandline as operation_function
    elif function_name == "geary": 
        from lib.descriptor_CLI_interfaces import gearyautocorrelationcommandline as operation_function
    elif function_name == "moreaubroto": 
        from lib.descriptor_CLI_interfaces import normalizedmoreaubrotoautocorrelationcommandline as operation_function
    elif function_name == "moran": 
        from lib.descriptor_CLI_interfaces import moranautocorrelationcommandline as operation_function
    elif function_name == "pseudoaacomp":
        from lib.descriptor_CLI_interfaces import pseudoaminoacidcompositioncommandline as operation_function
    elif function_name == "summary":
        from lib.descriptor_CLI_interfaces import summary as operation_function
    # "Supervised Learning":
    elif function_name == "svmtrain":
        from lib.supervised_learning import svmtrain as operation_function
    elif function_name == "svmclassify":
        from lib.supervised_learning import svmclassify as operation_function
    elif function_name == "linearRegression":
        from lib.supervised_learning import linearRegression as operation_function
    # "Unsupervised Learning"
    elif function_name == "dbscan":
        from lib.unsupervised_learning import DBSCAN as operation_function
    elif function_name == "kmeans":
        from lib.unsupervised_learning import kmeans as operation_function
    # Graph Operations
    elif function_name == "listedges":
        from lib.graph import listedges as operation_function

    return operation_function
