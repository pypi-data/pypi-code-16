from __future__ import division, print_function
from scipy import cos, sin, array, exp, conj, arcsin
from numpy.linalg import det
import numpy as np
import collections
import multiprocessing
import platform


# region Standard tmm solver

def solve_tmm(s, wls, pol, ang, eval_map=None):
    """
    Main entry point for solver using the standard transfer matrix method (tmm).
    :param s: stack of layers
    :param wls: wavelengths to evaluate
    :param pol: polarization
    :param ang: angle of incidence
    :param eval_map: custom function to evaluate
    :return: map of output
    """
    wls = _get_list(wls)
    eval_map = {} if eval_map is None else eval_map

    def func(i):
        return _process_coherent_block(wls[i], pol, pre_process(s, wls[i], ang), eval_map)

    return _sweep(func, len(wls))


def scan_E_tmm(s, wl, pol, ang, pts=None):
    """ Calculate electric field amplitudes across the structure """
    return _scan_stack_tmm(s, wl, pol, ang, pts, lambda i, pre, E: E)


def scan_E_vec_tmm(s, wl, pol, ang, pts=None):
    """ Calculate electric field vector across the structure """
    return _scan_stack_tmm(s, wl, pol, ang, pts, lambda i, pre, E: E_vec_from_E(E, pol, pre['ang'][i]))


def scan_flux_tmm(s, wl, pol, ang, pts=None):
    """ Calculate energy flux across the structure """
    return _scan_stack_tmm(s, wl, pol, ang, pts, lambda i, pre, E: _phi_from_E(pol, pre['n'], pre['ang'], E, i))


def scan_abs_tmm(s, wl, pol, ang, pts=None):
    """ Calculate absorption across the structure """
    return _scan_stack_tmm(s, wl, pol, ang, pts,
                           lambda i, pre, E: _abs_from_E(pre['k'][i], pol, pre['n'], pre['ang'], E, i))


def _scan_stack_tmm(s, wl, pol, ang, pts, func):
    """ TMM stack scanning interface """
    if len(_get_list(wl)) > 1:
        raise ValueError("Scanning interface does NOT support wavelength scans.")

    pre = pre_process(s, wl, ang)

    def inner_func(beta, i):
        return func(i, pre, np.dot(coherent_propagation_matrix(beta), res['E'][0][i]))

    res = solve_tmm(s, wl, pol, ang, {'E': eval_E_coherent})
    return _scan_stack(pre, inner_func, pts)


def layer_abs_tmm(s, wls, pol, ang):
    """ Absorption per layer """
    res = solve_tmm(s, wls, pol, ang, {'E': eval_E_coherent})
    return _layer_abs_spectral_sweep(s, wls, ang, res,
                                     lambda pre, j, i: _phi_from_E(pol, pre['n'], pre['ang'], res['E'][j][i], i))


def ellips_tmm(s, wls, ang):
    """ Parameters for ellipsometry, untested """
    solve_s = solve_tmm(s, wls, 's', ang)
    solve_p = solve_tmm(s, wls, 'p', ang)
    rs = array(solve_s['r'])
    rp = array(solve_p['r'])
    return np.arctan(abs(rp / rs)), np.angle(-rp / rs)


# endregion

# region Absolute coherence solver

def solve_asm(s, wls, pol, ang, coh_lst=None, eval_map=None):
    """
    Main entry point for solver using the absolute squares method (asm).
    :param s: stack of layers
    :param wls: wavelengths to evaluate
    :param pol: polarization
    :param ang: angle of incidence
    :param coh_lst: must contain an entry 'c' (coherent) or 'i' (incoherent) per layer in the stack
    :param eval_map: custom function to evaluate
    :return: map of output
    """
    wls = _get_list(wls)
    eval_map = {} if eval_map is None else eval_map

    # Inner method for actual asm calculation (called if all layers are NOT coherent)
    def _solve_asm():
        def func(i):
            pre = pre_process(s, wls[i], ang)
            return _process_incoherent_block(wls[i], pol, pre, ['c'] + coh_lst + ['c'], eval_map)

        return _sweep(func, len(wls))

    return _switch_asm(s, coh_lst, lambda: solve_tmm(s, wls, pol, ang, eval_map), _solve_asm)


def layer_abs_asm(s, wls, pol, ang, coh_lst=None):
    """ Absorption per layer """
    wls = _get_list(wls)

    def _layer_abs_asm():
        full_coh_lst = ['c'] + coh_lst + ['c']
        eval_map = {'U': lambda data, out_map: _eval_U_and_stuff(s, wls, pol, ang, data, out_map, full_coh_lst)}
        res = solve_asm(s, wls, pol, ang, coh_lst, eval_map)
        return _layer_abs_spectral_sweep(s, wls, ang, res, lambda pre, j, i: _eval_stuff(pre, full_coh_lst, res,
                                                                                         lambda pre, i, E: _phi_from_E(
                                                                                             pol, pre['n'], pre['ang'],
                                                                                             E, i),
                                                                                         lambda pre, i, U: _phi_from_U(
                                                                                             pol, pre['n'], pre['ang'],
                                                                                             U, i), 0, i, j))

    return _switch_asm(s, coh_lst, lambda: layer_abs_tmm(s, wls, pol, ang), _layer_abs_asm)


def scan_flux_asm(s, wl, pol, ang, coh_lst=None, pts=None):
    """ Calculate energy flux across the structure """

    def _scan_flux_asm():
        return _scan_stack_asm(s, wl, pol, ang, coh_lst, pts,
                               lambda pre, i, E: _phi_from_E(pol, pre['n'], pre['ang'], E, i),
                               lambda pre, i, U: _phi_from_U(pol, pre['n'], pre['ang'], U, i))

    return _switch_asm(s, coh_lst, lambda: scan_flux_tmm(s, wl, pol, ang, pts), _scan_flux_asm)


def scan_abs_asm(s, wl, pol, ang, coh_lst=None, pts=None):
    """ Calculate absorption across the structure """

    def _scan_abs_asm():
        return _scan_stack_asm(s, wl, pol, ang, coh_lst, pts,
                               lambda pre, i, E: _abs_from_E(pre['k'][i], pol, pre['n'], pre['ang'], E, i),
                               lambda pre, i, U: _abs_from_U(pre['k'][i], pol, pre['n'], pre['ang'], U, i))

    return _switch_asm(s, coh_lst, lambda: scan_abs_tmm(s, wl, pol, ang, pts), _scan_abs_asm)


def _scan_stack_asm(s, wl, pol, ang, coh_lst, pts, funcE, funcU):
    """ ASM stack scanning interface """
    if len(_get_list(wl)) > 1:
        raise ValueError("Scanning interface does NOT support wavelength scans.")

    pre = pre_process(s, wl, ang)
    full_coh_lst = ['c'] + coh_lst + ['c']
    eval_map = {'U': lambda data, out_map: _eval_U_and_stuff(s, wl, pol, ang, data, out_map, full_coh_lst)}
    res = solve_asm(s, wl, pol, ang, coh_lst, eval_map)
    return _scan_stack(pre, lambda beta, i: _eval_stuff(pre, full_coh_lst, res, funcE, funcU, beta, i), pts)


def _eval_stuff(pre, full_coh_lst, res, funcE, funcU, beta, i, j=0):
    if full_coh_lst[i] is 'c':
        m = coherent_propagation_matrix(beta)
        phi_l = funcE(pre, i, np.dot(m, res['E_p'][j][i]))
        phi_r = funcE(pre, i, np.dot(m, res['E_m'][j][i]))
        return phi_l + phi_r
    elif full_coh_lst[i] is 'i':
        return funcU(pre, i, np.dot(_incoherent_propagation_matrix(beta), res['U'][j][i]))
    else:
        raise ValueError('Value must be c or i')


def _eval_U_and_stuff(s, lmb, pol, ang, data, out, coh_lst):
    n = len(s) + 2
    pre = pre_process(s, _get_list(lmb)[0], ang)
    # Take into account a potential final coherent layer.
    incoh = [i for i, entry in enumerate(coh_lst) if entry is 'i']
    incoh_n = len(incoh) + 1
    # Allocate field lists (TODO: Allocate NaN instead?).
    U_list = np.zeros((n, 2), dtype=float)
    Ep_list = np.zeros((n, 2), dtype=complex)
    Em_list = np.zeros((n, 2), dtype=complex)
    # Calculate field amplitudes.
    U_list_full = _back_propagate_full(array([out['t_bar'], 0]), data['I_bar'], data['L_bar'])
    U_list[0] = U_list_full[0]
    offset = 0
    for i in np.arange(0, incoh_n):
        # For incoherent layers, just record U.
        idx = incoh[i] if i < len(incoh) else n - 1
        U_list[idx] = U_list_full[2 * (i + 1) if i < incoh_n - 1 else -1]
        # For coherent layer(s), the E-field must be reconstructed.
        if (idx - offset) > 1:
            # Calculate sub stack data.
            sub_pre = {key: pre[key][offset:idx + 1] if key is not 'lmb' else pre[key] for key in pre.keys()}
            data = _pre_process_coherent_block(pol, sub_pre)
            # Forward wave.
            E_iR = np.sqrt(U_list_full[2 * i + 0][0]) * array([_t_from_S(data['S']), 0])
            Ep_list[offset + 1:idx] = _back_propagate(E_iR, data['I'], data['L'])[1:-1]
            # Backward wave.
            E_jL = np.sqrt(U_list_full[2 * i + 1][1]) * array([_r_back_from_S(data['S']), 1])
            Em_list[offset + 1:idx] = _back_propagate(E_jL, data['I'], data['L'])[1:-1]
        # Update offset.
        offset = idx
    # Inject fields (HACK)
    out['E_p'] = Ep_list
    out['E_m'] = Em_list
    return U_list


def _switch_asm(s, coh_lst, func_tmm, func_asm):
    # No coherence information specified, fall back to coherent processing.
    if coh_lst is None:
        return func_tmm()
    # Coherence must be specified for all layers.
    elif len(coh_lst) is not len(s):
        raise ValueError('Length of coh_lst must equal length of stack.')
    # All layers are coherent, fall back to coherent processing.
    elif all(entry is 'c' for entry in coh_lst):
        return func_tmm()
    # Only 'c' (coherent) and 'i' (incoherent) are valid input arguments.
    elif all(entry is 'c' or 'i' for entry in coh_lst):
        return func_asm()
    else:
        raise ValueError('All entries in coh_lst must be c (coherent) or i (incoherent).')


# endregion

# region Phase average solver

def _switch_pam(s, dephase_lst, func_tmm, func_pam):
    # No coherence information specified, fall back to coherent processing.
    if dephase_lst is None:
        return func_tmm()
    # Coherence must be specified for all layers.
    elif len(dephase_lst) is not len(s):
        raise ValueError('Length of dephase_lst must equal length of stack.')
    # All layers are coherent, fall back to coherent processing.
    elif all(entry is 0 for entry in dephase_lst):
        return func_tmm()
    # Nonzero dephasing. Do phase averaging.
    elif all(0 <= entry <= 1 for entry in dephase_lst):
        return func_pam()
    else:
        raise ValueError('All entries in dephase_lst must be between 0 and 1.')


def solve_pam(s, wls, pol, ang, dephase_lst=None, runs=50, random=False, eval_map=None, agg_map=None):
    """
    Main entry point for solver based on the phase averaging method (pam).
    :param s: stack of layers
    :param wls: wavelengths to evaluate
    :param pol: polarization
    :param ang: angle of incidence
    :param dephase_lst: must contain a number between 0 (coherent) and 1 (incoherent) per layer in the stack
    :param runs: number of runs over which results are averaged (performance critical)
    :param random: if true, phases are chosen randomly otherwise uniformly
    :param eval_map: custom function to evaluate
    :param agg_map: aggregation of custom functions
    :return: map of output
    """
    wls = _get_list(wls)
    eval_map = {} if eval_map is None else eval_map
    agg_map = {} if agg_map is None else agg_map
    shifts = np.random.uniform(-np.pi / 2, np.pi / 2, runs) if random else np.linspace(-np.pi / 2, np.pi / 2, runs,
                                                                                       False)

    # Inner method for actual pam calculation (called if all layers are NOT coherent)
    def _solve_pam():
        def func(i):
            return _phase_avg(s, wls[i], pol, ang, [0] + dephase_lst + [0], runs, eval_map, agg_map, shifts)

        return _sweep(func, len(wls))

    return _switch_pam(s, dephase_lst, lambda: solve_tmm(s, wls, pol, ang, eval_map), _solve_pam)


def layer_abs_pam(s, wls, pol, ang, dephase_lst=None, avg_runs=1e3):
    eval_map = {'E': eval_E_coherent}
    agg_map = {'E': _agg_E_incoherent}
    wls = _get_list(wls)

    # Inner method for actual pam calculation (called if all layers are NOT coherent)
    def _layer_abs_pam():
        tmp_res = solve_pam(s, wls, pol, ang, dephase_lst, avg_runs, eval_map, agg_map)

        def func(pre, j, i):
            return _phi_from_E(pol, pre['n'], pre['ang'], tmp_res['E'][j][i], i)

        return _layer_abs_spectral_sweep(s, wls, ang, tmp_res, func)

    return _switch_pam(s, dephase_lst, lambda: layer_abs_tmm(s, wls, pol, ang), _layer_abs_pam())


# TODO: Instead of modifying the phase shift, the WEIGHTS of the different solutions should be modified
def _phase_avg(s, wl, pol, ang, dephase_lst, avg_runs, eval_map, agg_map, shifts):
    # Pre process structure.
    pre = pre_process(s, wl, ang)
    data = _pre_process_coherent_block(wl, pol, pre)
    n = len(pre['layers'])
    # Allocate tmp data structures.
    run_map = {}
    tmp_map = {}
    # Loop over (avg_runs number of) runs over which results are averaged.
    L_lst = np.empty((n - 1, 2, 2), dtype=complex)
    beta_lst = np.empty(n - 1, dtype=complex)
    for shift in shifts:
        # Calculate layer matrices for partially coherent layers.
        for i in np.arange(0, n - 1):
            j = i + 1
            if j < n - 1:
                if dephase_lst[j] is not 0:
                    beta_lst[j] = pre['d'][j] * pre['k'][j] + shift * dephase_lst[j]
                    L_lst[j] = coherent_propagation_matrix(-beta_lst[j])  # NOTE: Beta sign might be wrong
                else:
                    L_lst[j] = data['L'][j]
        # Calculate scattering matrix.
        S = np.eye(2, 2, dtype=complex)
        for i in np.arange(0, n - 1):
            j = i + 1
            S = np.dot(S, data['I'][i])
            if j < n - 1:
                S = np.dot(S, L_lst[j])
        # Inject new I, S entries to data object.
        data['S'] = S
        data['L'] = L_lst
        data['beta'] = beta_lst
        # Calculate reflection/transmission coefficients.
        run_map['r'] = _r_from_S(S)
        run_map['t'] = _t_from_S(S)
        run_map['R'] = _R_from_r(run_map['r']).real
        run_map['T'] = _T_from_t(run_map['t'], pre['n'][0], pre['n'][-1], pre['ang'][0], pre['ang'][-1], pol).real
        # Calculate any additional parameters.
        for key in eval_map.keys():
            run_map[key] = eval_map[key](data, run_map)
        # Save iteration results in tmp_map.
        for key in run_map.keys():
            if key not in pre:
                if key not in tmp_map:
                    tmp_map[key] = []
                tmp_map[key].append(run_map[key])
    # Create output.
    out = dict(pre)
    for key in tmp_map.keys():
        # Since custom values are of an unknown type, we cannot necessarily calculate the avg automatically.
        if key in agg_map:
            out[key] = agg_map[key](tmp_map[key])
        else:
            out[key] = np.sum(tmp_map[key], 0) / avg_runs
    return out


# endregion

# region Gaussian filter solver

def _switch_gfm(s, coh_len, func_tmm, func_gfm):
    # Infinite or unspecified coherence length, fall back to coherent processing.
    if coh_len is None or np.isinf(coh_len):
        return func_tmm()
    # Finite coherence length. Do spectral, gaussian averaging.
    elif coh_len > 0:
        return func_gfm()
    # Coherence length must be strictly positive.
    else:
        raise ValueError('The coh_len must be strictly positive.')


def solve_gfm(s, wls, pol, ang, coh_len=None, res=1e3, eval_map=None, agg_map=None):
    """
    Main entry point for solver the based on gaussian filter method (gfm).
    This method allows the treatment of light with a final (known) coherence length.
    :param s: stack of layers
    :param wls: wavelengths to evaluate
    :param pol: polarization
    :param ang: angle of incidence
    :param coh_len: coherence length of incoming light
    :param res: spectral resolution prior to averaging (performance critical)
    :param eval_map: custom function to evaluate
    :return: map of output
    """
    agg_map = {} if agg_map is None else agg_map
    eval_map = {} if eval_map is None else eval_map
    wls = _get_list(wls)

    return _switch_gfm(s, coh_len,
                       lambda: solve_tmm(s, wls, pol, ang, eval_map),
                       lambda: _gauss_spectral_avg(s, wls, pol, ang, coh_len, res, eval_map, agg_map))


def layer_abs_gfm(s, wls, pol, ang, coh_len=None, res=1e5):
    eval_map = {'E': eval_E_coherent}
    agg_map = {'E': _agg_E_incoherent}

    # Inner method for actual pam calculation (called if all layers are NOT coherent)
    def _layer_abs_gfm():
        tmp_res = solve_gfm(s, wls, pol, ang, coh_len, res, eval_map, agg_map)

        def func(pre, j, i):
            return _phi_from_E(pol, pre['n'], pre['ang'], tmp_res['E'][j][i], i)

        return _layer_abs_spectral_sweep(s, wls, ang, tmp_res, func)

    return _switch_pam(s, coh_len, lambda: layer_abs_tmm(s, wls, pol, ang), _layer_abs_gfm())


def _gauss_spectral_avg(s, wls, pol, ang, coh_len, res, eval_map, agg_map=None):
    # Evaluate results in a highly resolved grid (wave length).
    hd_wls = np.linspace(wls[0] - 2 / np.pi * wls[0] ** 2 / coh_len, wls[-1] + 2 / np.pi * wls[-1] ** 2 / coh_len, res)
    hd_res = solve_tmm(s, hd_wls, pol, ang, eval_map)
    out = {key: [] for key in hd_res}
    # Do gaussian averaging.
    for i in np.arange(0, len(wls)):
        mu = wls[i]
        sigma = 2 / np.pi * mu ** 2 / coh_len
        idx_min = np.searchsorted(hd_wls, mu - sigma)
        idx_max = np.searchsorted(hd_wls, mu + sigma)
        tmp_wls = hd_wls[idx_min:idx_max]
        gauss = 1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(- (tmp_wls - mu) ** 2 / (2 * sigma ** 2))
        weights = gauss / np.sum(gauss)
        # Some quantities can be aggregated easily, some needs special treatment (agg_map).
        for key in out:
            if key in agg_map.keys():
                out[key].append(agg_map[key](hd_res[key][idx_min:idx_max], weights))
            else:
                out[key].append(np.dot(hd_res[key][idx_min:idx_max], weights))
    return out


# endregion

# region Energy flux and absorption

def eval_E_coherent_full(data, out):
    """ Evaluate E field coherently """
    return _back_propagate_full(array([out['t'], 0]), data['I'], data['L'])


def eval_E_coherent(data, out):
    """ Evaluate E field coherently """
    return _back_propagate(array([out['t'], 0]), data['I'], data['L'])


def _agg_E_incoherent(data, weights=None):
    """ Aggregate E field incoherently """
    weights = np.ones(len(data)) / len(data) if weights is None else weights
    return np.sqrt(np.transpose(np.dot(np.transpose(abs(array(data)) ** 2), weights)))


def _layer_abs_spectral_sweep(s, wls, ang, tmp_res, func):
    """ Calculate absorption in each layer in the stack across range of wavelengths """
    out = []
    for j in np.arange(0, len(wls)):
        wl = wls[j]
        pre = pre_process(s, wl, ang)
        out.append(_layer_abs(pre, tmp_res['R'][j], tmp_res['T'][j], lambda i: func(pre, j, i)))
    return out


def _layer_abs(pre, R, T, func):
    """ Calculate absorption in each layer of the stack """
    layers = pre['layers']
    phi_layer = np.zeros(len(layers))
    phi_layer[1] = 1 - R
    phi_layer[-1] = T
    for i in np.arange(2, len(phi_layer)):
        phi_layer[i] = func(i - 1)
    abs_list = np.zeros(len(phi_layer))
    abs_list[0:-1] = -np.diff(phi_layer)
    abs_list[0] = R
    abs_list[-1] = T
    return abs_list


# endregion

# region Block processing

def _process_coherent_block(wl, pol, pre, eval_map):
    """ Calculate important quantities for coherent block """
    # Pre process structure.
    data = _pre_process_coherent_block(pol, pre)
    # Calculate reflection/transmission coefficients.
    out = {'r': _r_from_S(data['S']), 't': _t_from_S(data['S'])}
    out['R'] = _R_from_r(out['r']).real
    out['T'] = _T_from_t(out['t'], pre['n'][0], pre['n'][-1], pre['ang'][0], pre['ang'][-1], pol).real
    # Create custom output.
    for key in eval_map.keys():
        out[key] = eval_map[key](data, out)
    return out


def _pre_process_coherent_block(pol, pre):
    """ Calculate interface, layer and scattering matrices quantities for coherent block """
    n = len(pre['layers'])
    # Allocate coherent interface/layer matrices.
    I_lst = np.empty((n - 1, 2, 2), dtype=complex)
    L_lst = np.empty((n - 1, 2, 2), dtype=complex)
    beta_lst = np.empty(n - 1, dtype=complex)
    for i in np.arange(0, n - 1):
        j = i + 1
        # Coherent interface matrix.
        I_lst[i] = coherent_interface_matrix(pre['n'][i], pre['n'][j], pre['ang'][i], pre['ang'][j], pol)
        # Coherent propagation matrix.
        if j < n - 1:
            beta_lst[j] = pre['d'][j] * pre['k'][j]
            L_lst[j] = coherent_propagation_matrix(beta_lst[j])
    # Assemble scattering matrix.
    S = _assemble_s_matrix(I_lst, L_lst)

    return {'S': S, 'I': I_lst, 'L': L_lst, 'beta': beta_lst}


def _process_incoherent_block(wl, pol, pre, coh_lst, eval_map):
    # Pre process structure.
    data = _pre_process_incoherent_block(wl, pol, pre, coh_lst)
    out_map = {'r_bar': _r_from_S(data['S_bar']), 't_bar': _t_from_S(data['S_bar'])}
    # Calculate reflection/transmission coefficients.
    out_map['R'] = _R_from_r_bar(out_map['r_bar']).real
    out_map['T'] = _T_from_t_bar(out_map['t_bar'], pre['n'][0], pre['n'][-1], pre['ang'][0], pre['ang'][-1], pol).real
    # Create custom output.
    for key in eval_map:
        out_map[key] = eval_map[key](data, out_map)
    return out_map


def _pre_process_incoherent_block(wl, pol, pre, coh_lst):
    """ Calculate important quantities for incoherent blocks """
    n = len(pre['layers'])
    # Take into account a potential final coherent layer.
    incoh = [i for i, entry in enumerate(coh_lst) if entry is 'i']
    incoh_n = len(incoh) + 1
    # Allocate incoherent interface/layer matrices.
    I_bar_lst = np.zeros((incoh_n, 2, 2), dtype=float)
    L_bar_lst = np.zeros((incoh_n, 2, 2), dtype=float)
    offset = 0
    for i in np.arange(0, incoh_n):
        # Stop before reaching layer j.
        j = incoh[i] if i < len(incoh) else n - 1
        # Effective incoherent interface matrix.
        sub_pre = {key: pre[key][offset:j + 1] if key is not 'lmb' else pre[key] for key in pre.keys()}
        data = _pre_process_coherent_block(pol, sub_pre)
        I_bar_lst[i] = _incoherent_interface_matrix(data['S'])
        # Incoherent propagation matrix.
        if i < len(incoh):
            beta = phase_shift(wl, pre['d'][j], pre['n'][j], pre['ang'][j])
            L_bar_lst[i + 1] = _incoherent_propagation_matrix(beta)
        offset = j
    # Assemble scattering matrix.
    S_bar = _assemble_s_matrix(I_bar_lst, L_bar_lst)

    return {'S_bar': S_bar, 'I_bar': I_bar_lst, 'L_bar': L_bar_lst}


# endregion

# region Physics


def _incoherent_interface_matrix(S):
    """ Calculate incoherent interface matrix from coherent scattering matrix """
    return array([[abs(S[0, 0]) ** 2, -abs(S[0, 1]) ** 2],
                  [abs(S[1, 0]) ** 2, (abs(det(S)) ** 2 - abs(S[0, 1] * S[1, 0]) ** 2) / (abs(S[0, 0]) ** 2)]],
                 dtype=float)


def _incoherent_propagation_matrix(beta):
    """ Calculate incoherent propagation matrix from phase shift """
    if abs(beta.imag) > 25:
        beta = beta.real - 1.0j * 25
    return array([[abs(exp(1j * beta)) ** 2, 0], [0, abs(exp(- 1j * beta)) ** 2]], dtype=float)


def coherent_propagation_matrix(beta):
    """ Calculate coherent propagation matrix from phase shift """
    if abs(beta.imag) > 25:
        beta = beta.real - 1.0j * 25
    return array([[exp(1j * beta), 0], [0, exp(- 1j * beta)]], dtype=complex)


def coherent_interface_matrix(n_i, n_j, ang_i, ang_j, pol):
    """ Calculate coherent interface matrix """
    [r_ij, t_ij] = _fresnel(n_i, n_j, ang_i, ang_j, pol)
    return 1 / t_ij * array([[1, r_ij], [r_ij, 1]], dtype=complex)


def phase_shift(lmb, n, d, ang):
    """ Calculate phase shift """
    return d * _kz(lmb, n, ang)


def _kz(lmb, n, ang):
    """ Calculate z-component of wave vector """
    return 2 * np.pi * n / lmb * cos(ang)


def _fresnel(n_i, n_j, ang_i, ang_j, pol):
    """
    Calculate Fresnel coefficients. Sign conventions are:
    s-polarization; E_f*[0,1,0], E_b*[0,1,0]
    p-polarization; E_f*[cos(ang),0,-sin(ang)], E_b*[cos(ang),0,+sin(ang)]
    """
    if pol is 's':
        t_ij = (2 * n_i * cos(ang_i)) / (n_i * cos(ang_i) + n_j * cos(ang_j))
        r_ij = (n_i * cos(ang_i) - n_j * cos(ang_j)) / (n_i * cos(ang_i) + n_j * cos(ang_j))
    elif pol is 'p':
        t_ij = (2 * n_i * cos(ang_i)) / (n_i * cos(ang_j) + n_j * cos(ang_i))
        r_ij = (n_i * cos(ang_j) - n_j * cos(ang_i)) / (n_i * cos(ang_j) + n_j * cos(ang_i))
    else:
        raise ValueError('Invalid polarisation, {}, must be "s" or "p".'.format(pol))
    return r_ij, t_ij


def _snell(n_list, ang):
    """ Calculate angles using Snell's law. Note: Scipy is CORRECT, but numpy is faster (maybe also correct?) """
    # return np.arcsin(complex(n_list[0] * sin(ang)) / n_list)
    return arcsin(n_list[0] * sin(ang) / n_list)


def E_vec_from_E(E, pol, ang):
    """ Calculate electric field vector from amplitude vector, E (E[0] = forward, E[1] = backward) """
    E_vec = []
    ef_vec = [0, 1, 0] if pol is 's' else [+cos(ang), 0, -sin(ang)]
    eb_vec = [0, 1, 0] if pol is 's' else [+cos(ang), 0, +sin(ang)]
    for k in range(0, len(ef_vec)):
        E_vec.append(E[0] * ef_vec[k] + E[1] * eb_vec[k])
    return array(E_vec)


def _phi_from_E(pol, n_list, ang_list, E, j):
    """ Calculate energy flux phi from electric field E (E[0] = forward, E[1] = backward) """
    if pol is 's':
        return (conj(n_list[j] * cos(ang_list[j])) * (E[0] + E[1]) * conj(E[0] - E[1])).real / \
               (conj(n_list[0] * cos(ang_list[0]))).real
    elif pol is 'p':
        return (conj(n_list[j]) * cos(ang_list[j]) * (E[0] + E[1]) * conj(E[0] - E[1])).real / \
               (conj(n_list[0]) * cos(ang_list[0])).real
    else:
        raise ValueError('Invalid polarisation, {}, must be "s" or "p".'.format(pol))


def _phi_from_U(pol, n_list, ang_list, U, j):
    """ Calculate energy flux phi from electric field intensity U (U[0] = forward, U[1] = backward) """
    return (U[0] - U[1]) * _gamma(n_list[0], n_list[j], ang_list[0], ang_list[j], pol)


def _abs_from_E(kz, pol, n_list, ang_list, E, j):
    """ Calculate absorbed energy density abs_dens from electric field E (E[0] = forward, E[1] = backward) """
    if pol is 's':
        return ((-kz * abs(E[0] - E[1]) ** 2 + conj(kz) * abs(E[0] + E[1]) ** 2) *
                conj(n_list[j] * cos(ang_list[j]))).imag / conj(n_list[0] * cos(ang_list[0])).real
    elif pol is 'p':
        return ((-kz * abs(E[0] - E[1]) ** 2 + conj(kz) * abs(E[0] + E[1]) ** 2) *
                conj(n_list[j]) * cos(ang_list[j])).imag / (conj(n_list[0]) * cos(ang_list[0])).real
    else:
        raise ValueError('Invalid polarisation, {}, must be "s" or "p".'.format(pol))


def _abs_from_U(kz, pol, n_list, ang_list, U, j):
    """ Calculate absorbed energy density abs_dens from intensity U (U[0] = forward, U[1] = backward) """
    return - 2 * kz.imag * (U[0] + U[1]) * _gamma(n_list[0], n_list[j], ang_list[0], ang_list[j], pol)


def _t_from_S(S):
    """ Calculate complex transmission coefficient t (forward) from scattering matrix S """
    return 1 / S[0, 0]


def _t_back_from_S(S):
    """ Calculate complex transmission coefficient t from scattering matrix S """
    return np.linalg.det(S) / S[0, 0]


def _r_from_S(S):
    """ Calculate complex reflection coefficient r (forward) from scattering matrix S """
    return S[1, 0] / S[0, 0]


def _r_back_from_S(S):
    """ Calculate complex reflection coefficient r from scattering matrix S """
    return -S[0, 1] / S[0, 0]


def _R_from_r(r):
    """ Calculate power reflection coefficient R from complex reflection coefficient r """
    return _R_from_r_bar(abs(r) ** 2)


def _T_from_t(t, n_0, n, ang_0, ang, pol):
    """ Calculate power transmission coefficient T from complex transmission coefficient t """
    return _T_from_t_bar(abs(t) ** 2, n_0, n, ang_0, ang, pol)


def _R_from_r_bar(r_bar):
    """ Calculate power transmission coefficient T from complex reflection_bar coefficient r_bar """
    return r_bar


def _T_from_t_bar(t_bar, n_0, n, ang_0, ang, pol):
    """ Calculate power transmission coefficient T from complex transmission_bar coefficient t_bar """
    return t_bar * _gamma(n_0, n, ang_0, ang, pol)


def _gamma(n_0, n, ang_0, ang, pol):
    """ Calculate gamma factor """
    if pol is 's':
        return (conj(n * cos(ang))).real / (conj(n_0 * cos(ang_0))).real
    elif pol is 'p':
        return (conj(n) * cos(ang)).real / (conj(n_0) * cos(ang_0)).real
    else:
        raise ValueError('Invalid polarisation, {}, must be "s" or "p".'.format(pol))


# endregion

# region Util methods

def _assemble_s_matrix(I_list, L_list):
    data_type = type(I_list[0][0][0])
    S = np.eye(2, 2, dtype=data_type)
    for i in np.arange(0, len(I_list)):
        j = i + 1
        S = np.dot(S, I_list[i])
        if j < len(I_list):
            S = np.dot(S, L_list[j])
    return S


def _back_propagate_full(a_0, I_list, L_list):
    """
    Back propagate a_0 using I_list and L_list, save BOTH after interface AND layer propagation
    """
    data_type = type(I_list[0][0][0])
    a_list = np.zeros((len(I_list) * 2, 2), dtype=data_type)
    a_list[-1] = a_0
    j = len(a_list) - 2
    for i in range(len(I_list) - 1, -1, -1):
        a_list[j] = np.dot(I_list[i], a_list[j + 1])
        j -= 1
        if i > 0:
            a_list[j] = np.dot(L_list[i], a_list[j + 1])
            j -= 1
    return a_list


def _back_propagate(a_0, I_list, L_list):
    """
    Back propagate a_0 using I_list and L_list, save ONLY after layer + interface propagation
    """
    return np.array(list(_back_propagate_full(a_0, I_list, L_list)[::2]) + [a_0])


def pre_process(s, lmb, ang):
    return pre_process_layers(s.assemble(), lmb, ang)


def pre_process_layers(layers, lmb, ang):
    n_lst = array([l.material.get_complex_ri(lmb) for l in layers])
    d_lst = array([l.depth for l in layers])
    ang_lst = array(_snell(n_lst, ang))
    k_lst = array([_kz(lmb, n_lst[i], ang_lst[i]) for i, l in enumerate(layers)])
    return {'lmb': lmb, 'n': n_lst, 'ang': ang_lst, 'd': d_lst, 'k': k_lst, 'layers': layers}


def _scan_stack(pre, func, pts):
    """ Scan across layers in the stack
    :param pre: preprocessed stack
    :param func: function to evaluate
    :param pts: list of [idx, resolution] determining what layers are scanned and at what resolution
    :return: list of points (absolute position in s), list of values
    """
    pts = [[i + 1, 100] for i, l in enumerate(pre['layers'][1:-1])] if pts is None else pts
    n = np.sum([entry[1] for entry in pts])
    points = np.empty(n)
    values = []
    i = 0
    for entry in pts:
        j = entry[0]
        offset = np.sum([pre['d'][int(k)] for k in np.linspace(1, j, j - 1, False)])
        for point in np.linspace(pre['d'][j], 0, entry[1], False):
            points[i] = offset + (pre['d'][j] - point)
            beta = phase_shift(pre['lmb'], pre['n'][j], point, pre['ang'][j])
            values.append(func(beta, j))
            i += 1

    return points, values


def _sweep(func, n):
    if "Windows" in platform.system():
        return _sequential_sweep(func, n)
    else:
        return _parallel_sweep(func, n)


def _sequential_sweep(func, n):
    """ Sweep over variable(s)
    :type n: Total number of iterations in sweep
    :type func: function to evaluate at index
    :return: map of output
    """

    # Create lists.
    out_map = {}
    for i in np.arange(0, n):
        result = func(i)
        for key in result.keys():
            if i == 0:
                out_map[key] = []
            out_map[key].append(result[key])
    return out_map


def _parallel_sweep(func, n):
    """ Sweep over variable(s) (to be parallelised)
    :type n: Total number of iterations in sweep
    :type func: function to evaluate at index
    :return: map of output
    """

    # Create lists.
    result = func(0)
    out_map = {}
    for key in result.keys():
        out_map[key] = [result[key]]
    # Evaluate result in parallel.
    results = parmap(func, range(1, n))
    for i in np.arange(1, n):
        for key in out_map:
            out_map[key].append(results[i - 1][key])
    # Create output.
    return out_map


def _get_iterable(x):
    return x if isinstance(x, collections.Iterable) else x,


def _get_list(x):
    if isinstance(x, (list, tuple)):
        return x
    elif isinstance(x, np.ndarray):
        return list(x)  # Fixes problems with numpy arrays
    else:
        return [x]


# endregion

# region Parallel hack

def fun(f, q_in, q_out):
    while True:
        i, x = q_in.get()
        if i is None:
            break
        q_out.put((i, f(x)))


def parmap(f, X, nprocs=multiprocessing.cpu_count()):
    q_in = multiprocessing.Queue(1)
    q_out = multiprocessing.Queue()

    proc = [multiprocessing.Process(target=fun, args=(f, q_in, q_out)) for _ in range(nprocs)]
    for p in proc:
        p.daemon = True
        p.start()

    sent = [q_in.put((i, x)) for i, x in enumerate(X)]
    [q_in.put((None, None)) for _ in range(nprocs)]
    res = [q_out.get() for _ in range(len(sent))]

    [p.join() for p in proc]

    return [x for i, x in sorted(res)]


# endregion

# region External utils

def project(points, values, pre):
    layer = 1
    offset = 0
    for i in np.arange(0, len(points)):
        # Project value.
        values[i] *= np.cos(pre['ang'][layer])
        # Go to next layer
        if points[i] >= (offset + pre['d'][layer]):
            offset = offset + pre['d'][layer]
            layer += 1
    return points, values

# endregion
