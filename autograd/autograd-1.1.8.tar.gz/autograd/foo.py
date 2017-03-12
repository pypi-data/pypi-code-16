
    def log_Z(natural_params):
        init_params, pair_params, node_params = natural_params

        def unit(J, h, logZ):
            return (J, h), logZ

        def bind(result, step):
            message, lognorm = result
            new_message, term = step(message)
            return new_message, lognorm + term

        steps = interleave(map(condition, node_params), map(predict, pair_params))
        message, lognorm = monad_runner(bind, unit(*init_params), steps)
        lognorm = lognorm + natural_lognorm(message)

        return lognorm

    def monad_runner(bind, result, steps):
        for step in steps:
            result = bind(result, step)
        return result

    kalman_smoother = grad(log_Z)

    import autograd.numpy as np
    from autograd.scipy.linalg import solve_triangular
    from toolz import curry

    @curry
    def condition(node_param, message):
        J, h = message
        J_node, h_node, log_Z_node = node_param
        return (J + J_node, h + h_node), log_Z_node

    @curry
    def predict(pair_param, message):
        J, h = message
        J11, J12, J22, log_Z_pair = pair_param
        L = np.linalg.cholesky(-2*(J + J11))
        v = solve_triangular(L, h)
        lognorm = 1./2 * np.dot(v, v) - np.sum(np.log(np.diag(L)))
        h_predict = np.dot(J12.T, solve_triangular(L, v, trans='T'))
        temp = solve_triangular(L, J12)
        J_predict = J22 + 1./2 * np.dot(temp.T, temp)
        return (J_predict, h_predict), lognorm + log_Z_pair
