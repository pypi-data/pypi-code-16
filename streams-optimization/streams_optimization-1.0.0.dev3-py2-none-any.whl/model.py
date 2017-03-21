import numpy as np
import theano.tensor as T
import theano
import lasagne


def compute_T_score(event_line_matrix, L_matrix, prescale):  # first error metrics(Tuesday, 30.06)
    """
    Computes T score of current streaming scheme "L" on dataset "event_line_matrix".

    Parameters
    ----------
    event_line_matrix : numpy.ndarray of type bool or Theano.matrix
        Matrix that shows event-line correspondence.
    L_matrix : numpy.ndarray of type float or bool or Theano.matrix
        Matrix that shows line-stream correspondence probability. Every row should sum up to 1.
    prescale : numpy.array of type float
        Array that contains prescale value for each line.

    Returns
    -------
    float
        T score normalized to it's optimal value (every line has its own stream).

    """

    prescaled_event_line_matrix = event_line_matrix * prescale
    optimal_loss = prescaled_event_line_matrix.sum()
    event_line_stream = prescaled_event_line_matrix[:, :, None] * L_matrix[None, :, :]
    event_in_stream = 1 - (1 - event_line_stream).prod(axis=1)
    events_per_stream = event_in_stream.sum(axis=0)
    lines_per_stream = L_matrix.sum(axis=0)
    time_per_stream = lines_per_stream * events_per_stream
    return time_per_stream.sum() / optimal_loss


def iteratively_compute_T_score_per_stream(event_line_matrix, L_matrix, prescale):
    """
    Computes T score of current streaming scheme "L" on dataset "event_line_matrix".

    Parameters
    ----------
    event_line_matrix : numpy.ndarray of type bool or Theano.matrix
        Matrix that shows event-line correspondence.
    L_matrix : numpy.ndarray of type float or bool or Theano.matrix
        Matrix that shows line-stream correspondence probability. Every row should sum up to 1.
    prescale : numpy.array of type float
        Array that contains prescale value for each line.

    Returns
    -------
    float
        T score normalized to it's optimal value (every line has its own stream).

    """

    prescaled_event_line_matrix = event_line_matrix.dot(np.diag(prescale))
    optimal_loss = prescaled_event_line_matrix.sum()
    n_events = event_line_matrix.shape[0]
    n_streams = L_matrix.shape[1]
    _event_in_stream = np.zeros((n_events, n_streams))
    for i in range(n_events):
        for j in range(n_streams):
            _event_in_stream[i, j] = (1 - (prescaled_event_line_matrix[i, :] *
                                      L_matrix[:, j])).prod()
    event_in_stream = 1 - _event_in_stream
    events_per_stream = event_in_stream.sum(axis=0)
    lines_per_stream = L_matrix.sum(axis=0)
    time_per_stream = lines_per_stream * events_per_stream
    return time_per_stream / optimal_loss


def compile_theano_functions(n_lines,
                             n_streams,
                             random_initialization,
                             update_function=lasagne.updates.adamax,
                             loss_function=compute_T_score,
                             **kwargs
                             ):
    """
    Builds and compiles theano functions for gradient optimization process. Self-chosen random initialization,
    update function or loss function can be used, but it should meet the requirements listed below.

    Parameters
    ----------
    n_lines : int
        Number of lines in processing data (e.g. in line_stream_matrix)
    n_streams : int
        Number of streams in processing data (e.g. in line_stream_matrix)
    random_initialization : function(<size>) -> random matrix of size <size>
        Generates random matrix with the requested size.
    update_function : lasagne.updates function or equivalent
        "Loss or grads" function to compute the gradient of loss score.
    loss_function : function(<event_line_matrix, L_matrix, **kwargs>) -> loss score
        Computes the loss score according to the problem being solved. By default computes T score.
        Additional arguments are being passed as dict using **kwargs.
    **kwargs : optional dict {<argument name>: <argument value>}
        Dictionary that contains additional arguments for loss function.

    Returns
    -------
    update_func : function(<event_line_matrix or alike>)->loss score of type float
        Compiled theano function that updates the shared variables, making a gradient step to minimize the loss score.
        As argument takes event_line_matrix or it's part (minibatch) to compute the gradient.
    eval_func : function(<event_line_matrix or alike>)->[relaxed_loss, deterministic_loss]
        relaxed_loss is a loss score computed using relaxed_line_stream_matrix by loss_function, and deterministic_loss
        - using deterministic_line_stream_matrix accordingly.
    relaxed_line_stream_matrix : theano.matrix of type float
        Matrix with probabilities of line-to-stream correspondence. Can be passed to theano functions. To get values
        for future processing use ".eval()" (e.g. "L = relaxed_line_stream_matrix.eval()").
    deterministic_line_stream_matrix : theano.matrix of type bool
        Matrix with strict line-to-split correspondence. Line is assigned to stream with highest probability in
        relaxed_line_stream_matrix. Can be passed to theano functions. To get values
        for future processing use ".eval()" (e.g. "L_det = deterministic_line_stream_matrix.eval()").
    """
    A = theano.shared(random_initialization((n_lines, n_streams)))
    relaxed_line_stream_matrix = T.nnet.softmax(A)
    theano_event_line_matrix = T.matrix("[event_i,line_i]matrix", dtype='int8')

    loss = loss_function(theano_event_line_matrix, relaxed_line_stream_matrix, **kwargs)

    stream_of_line = T.argmax(relaxed_line_stream_matrix, axis=1)

    deterministic_line_stream_matrix = T.zeros_like(A, dtype='uint32')
    deterministic_line_stream_matrix = T.set_subtensor(deterministic_line_stream_matrix[T.arange(n_lines),
                                                                                        stream_of_line], 1)

    det_loss = loss_function(theano_event_line_matrix, deterministic_line_stream_matrix, **kwargs)

    eval_fun = theano.function([theano_event_line_matrix], [loss, det_loss], on_unused_input='ignore')

    A_updates = update_function(loss, [A])

    A_updates[A] -= A.mean(axis=1, keepdims=1)

    update_func = theano.function([theano_event_line_matrix], loss, updates=A_updates, on_unused_input='ignore')
    return update_func, eval_fun, relaxed_line_stream_matrix, deterministic_line_stream_matrix


def get_scheme(event_line_matrix,
               n_streams,
               seed=42,
               evaluation_frequency=200,
               n_iterations=1001,
               batch_size=1000,
               random_initialization=lambda size_: np.random.uniform(low=-1,
                                                                     high=1,
                                                                     size=size_).astype(np.float64),
               update_function=lasagne.updates.adamax,
               loss_function=compute_T_score,
               **kwargs
               ):
    """

    Parameters
    ----------
    event_line_matrix : numpy.ndarray of type bool
        Matrix that shows event-line correspondence.
    n_streams : int
        Number of streams in processing data (e.g. in line_stream_matrix)
    seed : int
        Random seed for random numbers generator.
    evaluation_frequency : int
        Frequency of computing midterm T score to observe the path of optimization and store local best result.
    n_iterations : int
        Number of gradient steps.
    batch_size : int
        Number of events in batch used to compute gradient.
    random_initialization : function(<size>) -> random matrix of size <size>
        Generates random matrix with the requested size.
    update_function : lasagne.updates function or equivalent
        "Loss or grads" function to compute the gradient of loss score.
    loss_function : function(<event_line_matrix, L_matrix, **kwargs>) -> loss score
        Computes the loss score according to the problem being solved. By default computes T score.
        Additional arguments are being passed as dict using **kwargs.
    **kwargs : optional dict {<argument name>: <argument value}
        Dict that contains additional arguments for loss function.

    Returns
    -------
    relaxed_learning_curve : list of floats
        List with relaxed loss score for every evaluation step (n_iterations / evaluation_frequency steps), where
        relaxed loss is a loss score computed using relaxed_line_stream_matrix by loss_function.
    deterministic_learning_curve : list of floats
        List with deterministic loss score for every evaluation step (n_iterations / evaluation_frequency steps), where
        deterministic loss is a loss score computed using deterministic_line_stream_matrix accordingly.
    relaxed_line_stream_matrix : np.ndarray of type float
        Matrix with probabilities of line-to-stream correspondence.
    deterministic_line_stream_matrix : np.ndarray of type bool
        Matrix with strict line-to-split correspondence. Line is assigned to stream with highest probability in
        relaxed_line_stream_matrix.
    best_deterministic_score : float
        Best deterministic loss score obtained during optimization process.
    best_deterministic_line_stream_matrix : np.ndarray of type bool
        deterministic_line_stream_matrix corresponding to the best deterministic loss score.
    """
    np.random.seed(seed)
    n_events, n_lines = event_line_matrix.shape
    print (n_lines, n_streams)
    update_func, eval_fun, L, L_det = compile_theano_functions(n_lines,
                                                               n_streams,
                                                               random_initialization,
                                                               update_function,
                                                               loss_function,
                                                               **kwargs
                                                               )

    relaxed_learning_curve = []
    deterministic_learning_curve = []
    first_in_flag = True
    for i in range(n_iterations):
        events_minibatch = event_line_matrix[np.random.randint(low=0, high=n_events, size=batch_size)]
        update_func(events_minibatch)
        if i % evaluation_frequency == 0:
            relaxed_loss_i, det_loss_i = eval_fun(event_line_matrix)
            relaxed_learning_curve.append(float(relaxed_loss_i))
            deterministic_learning_curve.append(float(det_loss_i))

            if first_in_flag:
                best_deterministic_score = float(det_loss_i)
                best_deterministic_line_stream_matrix = L_det.eval()
                first_in_flag = False
            elif float(det_loss_i) < best_deterministic_score:
                best_deterministic_score = float(det_loss_i)
                best_deterministic_line_stream_matrix = L_det.eval()

    relaxed_line_stream_matrix = L.eval()
    deterministic_line_stream_matrix = L_det.eval()
    return [relaxed_learning_curve,
            deterministic_learning_curve,
            relaxed_line_stream_matrix,
            deterministic_line_stream_matrix,
            best_deterministic_score,
            best_deterministic_line_stream_matrix]