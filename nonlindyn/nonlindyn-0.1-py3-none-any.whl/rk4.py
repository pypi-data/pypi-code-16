

import numpy as np
import itertools

def rk4yield(f, xinit, start=0.0, step=None, raster=1):
    """
    Generator function for the Runge Kutta algorithm in autonomous case.
    
    Parameters
    ----------
    f : 
        function to integrate
    xinit : 
        starting position
    start : float
        starting time (optional)
    step : float
        timestep between outputs
    raster : int
        number of steps performed between two outputs (optional)
        
    Returns
    -------
    generator 
    
    Yields
    ------
    (t, x) : (float, vector)
        next point after applying an RK4 step
    
    Example
    -------
    >integrator = rk4yield(lambda xy: (xy[1], -xy[0]), (0.0, 1.0), step=0.1)
    >next(integrator), next(integrator)
    
    """
    
    # we need to be able to use array operations on `x` and the return of `f(x)`
    # let us convert both to numpy arrays
    x = np.array(xinit)
    fnp = lambda x:np.array(f(x)) 
    
    for t in itertools.count(start, step):
        yield t, x.copy()         # we need to give back a copy as we keep modifying x
        h = step/raster
        for i in range(raster):            
            # the "local time" could be calculated as 
            # t_local = t + i * h
            k1 = fnp(x)
            k2 = fnp(x + h/2.0 * k1)
            k3 = fnp(x + h/2.0 * k2)
            k4 = fnp(x + h * k3)
            x +=  h/6.0 * (k1 + 2*k2 + 2*k3 + k4)
            
                
def rk4trajectory(*args, **kwargs):
    """
    Wrapper for rk4yield which gives back full trajectory
    
    Parameters
    ----------
    f, xinit, start, step, raster : see rk4yield
    
    stop : float
        stop iteration, if current time is within half timestep 
        of stop. 
        
    *args, **kwargs
        all other parameters of rk4yield() can be used.
        
    Returns
    -------
    (t, x) : 
        t and x are arrays for time and phase space points at 
        each time step.
        
    Raises
    ------
        ValueError() if no valid stop is given. 
        
    Example
    -------
    Integrate a complete circle, and check how accurately we return to the starting point:
    >rk4trajectory(lambda xy: (xy[1], -xy[0]), (0.0, 1.0), step=2*np.pi/100, stop=2*np.pi )[-1][-1]    
    """
    start = kwargs.get("start", 0.0)
    stop = kwargs.pop("stop")
    step = kwargs["step"]
    
    if not ( 0 < (stop-start)/step < float("inf") ):
        raise ValueError("'stop' cannot be reached in a finite number of steps")
    
    integrator = itertools.takewhile(lambda txv : (txv[0]-stop)/step < 1/2, rk4yield(*args, **kwargs))
    T, X = zip(*integrator)
    return np.array(T), np.array(X)


