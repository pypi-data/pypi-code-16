"""State estimator that calls procedures for visualization or debugging"""

import seFast
reload(seFast)

observationHook = None
"""Procedure that takes two arguments, an observation and an
observation model, and does some useful display.  If ``None``, then
no display is done."""

beliefHook = None
"""Procedure that takes one argument, a belief distribution, and
does some useful display.  If ``None``, then no display is done.""" 

class StateEstimator(seFast.StateEstimator):
    """By default, this is the same as ``seFast.StateEstimator``.  If
    the attributes ``observationHook`` or ``beliefHook`` are defined,
    then as well as doing ``getNextValues`` from
    ``seFast.StateEstimator``, it calls the hooks.
    """
    def getNextValues(self, state, inp):
        if observationHook and inp:
            observationHook(inp[0], self.model.observationDistribution)
            
        result = seFast.StateEstimator.getNextValues(self, state, inp)
        
        if beliefHook:
            beliefHook(result[0])
            
        return result
