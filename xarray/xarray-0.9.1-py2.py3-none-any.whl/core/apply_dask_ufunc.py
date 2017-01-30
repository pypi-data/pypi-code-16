
def _deep_unpack_list(arg):
    if isinstance(arg, list):
        arg, = arg
        return _deep_unpack_list(arg)
    return arg


def apply_dask_ufunc(func, *args, **kwargs):
    import dask.array as da
    import toolz  # required dependency of dask.array

    signature = kwargs.pop('signature')
    dtype = kwargs.pop('dtype', None)
    if kwargs:
        raise TypeError('apply_dask_ufunc() got unexpected keyword '
                        'arguments: %s' % list(kwargs))

    if not all(isinstance(arg, da.Array) for arg in args):
        raise NotImplementedError(
            "dask_array='auto' currently requires only supports dask arrays "
            'if all arguments are dask arrays')
    if signature.n_outputs != 1:
        raise NotImplementedError(
            "cannot yet use dask_array='auto' with functions that "
            'return multiple values')
    if signature.all_output_core_dims - signature.all_input_core_dims:
        raise NotImplementedError(
            "cannot yet use dask_array='auto' with functions that create "
            'new dimensions')

    broadcast_dims = [tuple(range(arg.ndim - len(core_dims))[::-1])
                      for arg, core_dims
                      in zip(args, signature.input_core_dims)]
    input_dims = [bc_dims + core_dims
                  for bc_dims, core_dims
                  in zip(broadcast_dims, signature.input_core_dims)]

    n_broadcast_dims = max(len(dims) for dims in broadcast_dims)
    output_dims = [tuple(range(n_broadcast_dims))[::-1] + core_dims
                   for core_dims in signature.output_core_dims]

    dropped = signature.all_input_core_dims - signature.all_output_core_dims
    for arg, dims in zip(args, input_dims):
        for dropped_dim in dropped:
            if (dropped_dim in dims and
                    len(arg.chunks[dims.index(dropped_dim)]) != 1):
                raise ValueError('dimension %r dropped in the output does not '
                                 'consist of exactly one chunk on all arrays '
                                 'in the inputs' % dropped_dim)

    out_ind, = output_dims  # only one output currently supported
    atop_args = [b for a in (args, input_dims) for b in a]
    func2 = toolz.functoolz.compose(func, _deep_unpack_list)
    return da.atop(func2, out_ind, *atop_args, dtype=dtype)
