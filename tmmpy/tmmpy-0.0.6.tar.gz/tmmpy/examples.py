import matplotlib.pyplot as plt
from .tmmpy_core import *
from .tmmpy_objects import *


# region Coherent examples

def anti_reflection_coating():
    """ Perfect anti reflection coating (quarter wave layer) at normal incidence, angular dependence """
    s = Stack()
    res = 250
    lmb = 500
    n = 1.5

    # Calculate data.
    s.right = Material(n, 0)
    s.append(Layer(Material(np.sqrt(n), 0), lmb / 4 / np.sqrt(n)))
    ang_lst = np.linspace(0, np.pi, res)
    result = [solve_tmm(s, lmb, 's', ang)['T'] for ang in ang_lst]
    # Plot stuff.
    plt.plot(ang_lst / np.pi, result)
    plt.xlabel('$\\theta$ [$\pi$]')
    plt.ylabel('T [1]')


def high_reflection_coating():
    """ Figure 3.16 in Chapter 3, Thin Films """
    res = 250
    lmb = 500

    def do_stuff(n1, n2, lmb, res, N):
        # Prepare structure.
        s = Stack()
        for i in np.arange(0, N):
            s.append(Layer(Material(n1, 0), lmb / 4 / n1))
            s.append(Layer(Material(n2, 0), lmb / 4 / n2))
        # Calculate data.
        period = np.linspace(0, 2, res)
        R_lst = []
        for i in np.arange(0, res):
            for j in np.arange(0, N):
                s[j * 2].depth = lmb / 4 / n1 * period[i]
                s[j * 2 + 1].depth = lmb / 4 / n2 * period[i]
            result = solve_tmm(s, lmb, 's', 0)
            R_lst.append(result['R'])
        # Plot stuff.
        plt.plot(period, R_lst)

    def style():
        plt.ylabel('R [1]')
        plt.xlabel('Period [$\lambda$]')
        plt.tight_layout()

    # Example 1: n = 1.5
    plt.subplot(1, 2, 1)
    do_stuff(1.5, 1, lmb, res, 3)
    do_stuff(1.5, 1, lmb, res, 10)
    style()
    # Example 2: n = 3.5
    plt.subplot(1, 2, 2)
    do_stuff(3.5, 1, lmb, res, 3)
    do_stuff(3.5, 1, lmb, res, 10)
    style()


def high_reflection_coating_E_field():
    """ Figure 3.17 in Chapter 3, Thin Films """
    lmb = 500

    def do_stuff(n1, n2, lmb, period, N):
        unit = (lmb / 4 / n1 + lmb / 4 / n2)*period
        # Prepare structure.
        s = Stack()
        s.append(Layer(Material(1, 0), 5 * unit))
        for i in np.arange(0, N):
            s.append(Layer(Material(n1, 0), lmb / 4 / n1 * period))
            s.append(Layer(Material(n2, 0), lmb / 4 / n2 * period))
        s.append(Layer(Material(1, 0), 5 * unit))
        # Calculate data.
        [points, vals] = scan_E_tmm(s, lmb, 's', 0)
        plt.plot(array(points) / unit, [abs(val[0] + val[1]) ** 2 for val in vals])
        plt.xlim(0, 20)
        # Styling.
        plt.ylabel('|E|$^2$')
        plt.xlabel('$z$ [period]')
        plt.tight_layout()

    plt.subplot(2, 2, 1)
    do_stuff(1.5, 1, lmb, 0.7636, 10)
    plt.subplot(2, 2, 2)
    do_stuff(1.5, 1, lmb, 0.8086, 10)
    plt.subplot(2, 2, 3)
    do_stuff(1.5, 1, lmb, 0.8378, 10)
    plt.subplot(2, 2, 4)
    do_stuff(1.5, 1, lmb, 1, 10)


def fabry_perot_ethalon():
    """ Figure 3.12 in Chapter 3, Thin Films """
    s = Stack()
    res = 250
    lmb = 500
    ds = np.linspace(0, 2 * np.pi, res)

    def do_stuff(s, n, lmb, res):
        # Calculate data.
        s[0].material.set_ri(n)
        d_lst = lmb / (2 * np.pi * n) * ds
        R_lst = []
        T_lst = []
        for i in np.arange(0, res):
            s[0].depth = d_lst[i]
            result = solve_tmm(s, lmb, 's', 0)
            R_lst.append(result['R'])
            T_lst.append(result['T'])
        return np.pi * n, R_lst, T_lst

    def style():
        # plt.legend()
        plt.ylim(0, 1)
        plt.xlabel('$\Phi$ [$\pi$]')
        plt.tight_layout()

    s.append(Layer(Material(0, 0), 0))
    d4, r4, t4 = do_stuff(s, 4, lmb, res)
    d35, r35, t35 = do_stuff(s, 35, lmb, res)
    # Transmission plot.
    plt.subplot(1, 2, 1)
    plt.plot(ds/np.pi, t4, label='T, n = 4')
    plt.plot(ds/np.pi, t35, label='T, n = 35')
    plt.ylabel('T [1]')
    style()
    # Reflection plot.
    plt.subplot(1, 2, 2)
    plt.plot(ds/np.pi, r4, label='R, n = 4')
    plt.plot(ds/np.pi, r35, label='R, n = 35')
    plt.ylabel('R [1]')
    style()


def external_internal_reflection():
    """ Figure 3.9 in Chapter 3, Thin Films """
    s = Stack()
    res = 250
    lmb = 500

    def do_stuff(s, n1, n2, lmb, res, tag):
        # Calculate data.
        ang_lst = np.linspace(0, np.pi / 2, res)
        s.left = Material(n1, 0)
        s.right = Material(n2, 0)
        result_s = [solve_tmm(s, lmb, 's', ang)['r'] for ang in ang_lst]
        result_p = [solve_tmm(s, lmb, 'p', ang)['r'] for ang in ang_lst]
        # Plot stuff.
        plt.plot(ang_lst / np.pi * 180, abs(array(result_s)), label='{}, s'.format(tag))
        plt.plot(ang_lst / np.pi * 180, abs(array(result_p)), label='{}, p'.format(tag))

    do_stuff(s, 1, 1.5, lmb, res, 'External')
    do_stuff(s, 1.5, 1, lmb, res, 'Internal')
    plt.legend()
    plt.xlim(0, 90)
    plt.ylim(0, 1)


# endregion
