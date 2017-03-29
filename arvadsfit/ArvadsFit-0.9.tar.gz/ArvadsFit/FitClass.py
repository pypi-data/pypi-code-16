import numpy as np
from iminuit import Minuit, describe
from probfit import Chi2Regression


class Fit:
    def __init__(self, function, xdata, ydata, **kwargs):
        '''This class is used to fit an awesome function'''
        try:
            parnames = describe(function)[1:]
        except ValueError,e:
            print 'Remember that the variable must come before the parameters in your function definition.'
            print "I.e. given a,b,c as optimization parameters, define f(x,a,b,c) and not f(a,x,b,c)."
        else:
            self.fnc = function
            self.x, self.y = [np.array(t) for t in zip(*sorted(zip(xdata, ydata)))]
            self.yerr = np.ones(len(self.y))
            self.weights = np.ones(len(self.y))
            nparams = len(parnames)
            p0list = [1.] *nparams
            boundlist = [(None, None)] *nparams
            stepsize = [1.] *nparams
            self.parlist = []
            self.range = None
            self.DegreesOfFreedom = len(ydata) - nparams
            self.Chi2 = None
            self.residuals = 0
            self.assymetricalErrors = False
            self.fitresult = None
            self.verbose = False

            for key in kwargs:
                if key == "p0":
                    p0list = kwargs[key]
                elif key == "fitrange":
                    self.range = kwargs[key]
                elif key == "bounds":
                    boundlist = kwargs[key]
                elif key == "yerror":
                    self.yerr = np.array(kwargs[key])
                elif key=="AsymErrors":
                    self.assymetricalErrors = kwargs[key]
                elif key=='StepSize':
                    stepsize = kwargs[key]
                elif key=='weights':
                    self.weights =np.array(kwargs[key])
                elif key == 'Verbose':
                    self.verbose = kwargs[key]
            for i in range(nparams):
                self.parlist.append(
                    internalParameter(parnames[i], p0list[i], p0list[i], boundlist[i],stepsize[i]))

    def plot(self):
        x = np.linspace(min(self.x), max(self.x), 1000)
        y = self.fnc(x, *[k.Value() for k in self.parlist])
        return [x, y]

    def __call__(self, xvalue):
        return self.fnc(xvalue, *[k.Value() for k in self.parlist])

    def setParNames(self, lst):
        if len(lst) is self.nparam:
            for i in range(len(self.parlist)):
                self.parlist[i].Name(lst[i])

    def sqr(self, a):
        return a * a

    def mean(self, a):
        return sum(a) / float(len(a))

    def calcChi2(self):
        sm = 0.0
        params = [k.Value() for k in self.parlist]
        for i in range(len(self.y)):
            sm += self.sqr(self.y[i] - self.fnc(self.x[i],
                                                *params)) / self.sqr(self.yerr[i])
        self.Chi2 = sm

    def GetChisquare(self):
        '''Returns chi2 of the fit'''
        if self.fitresult is not None:
            return self.fitresult.fval
        else:
            return -1

    def GetNDof(self):
        '''Returns number of degrees of freedom for the fit'''
        return self.DegreesOfFreedom

    def setParLimit(self, parameter, mn, mx):
        '''Set parameter limits of a parameter'''
        self.parlist[parameter].Bounds((mn, mx))

    def std(self, a):
        sum = 0
        for i in range(len(a)):
            sum += self.sqr(a[i] - self.mean(a))
        return np.sqrt(sum / float(len(a)))

    def fit(self):
        self.savelist = []
        if self.range is not None:
            idxmin = (np.abs(self.x - self.range[0])).argmin()
            idxmax = (np.abs(self.x - self.range[1])).argmin()
            self.x = np.array(self.x[idxmin:idxmax + 1])
            self.y = np.array(self.y[idxmin:idxmax + 1])
            self.yerr = np.array(self.yerr[idxmin:idxmax + 1])
            self.weights = np.array(self.weights[idxmin:idxmax+1])
        chi2 = Chi2Regression(self.fnc,self.x,self.y,self.yerr,self.weights)

        args = {name:initval for (name,initval) in ((k.Name(),k.Initialvalue()) for k in self.parlist)}


        if any([k.Ifbound() for k in self.parlist]):
            bounds = {'limit_'+name:bound for (name,bound) in ((k.Name(),k.Bounds()) for k in self.parlist)}
            if self.verbose:
                print "Some parameters are limited:"
                for apar in self.parlist:
                    if apar.Ifbound():
                        print "{:s} ({:}, {:})".format(apar.Name(), *apar.Bounds())
            args.update(bounds)

        args.update({'print_level':0})
        if self.verbose:
            args.update({'print_level':1})
        steps = {'error_' +name:step for (name,step) in ((k.Name(),k.StepSize()) for k in self.parlist)}
        args.update(steps)

        minimizer = Minuit(chi2,**args)

        minimizer.migrad()
        if not minimizer.get_fmin().is_valid:
            print minimizer.get_fmin()
        else:
            if self.assymetricalErrors:
                minimizer.minos()


            for akey,avalue in minimizer.values.iteritems():
                for apar in self.parlist:
                    if apar.Name() == akey:
                        apar.Value(avalue)
                        #print avalue,minimizer.errors[akey]
                        if self.assymetricalErrors:
                            apar.Error([minimizer.get_merrors()[akey].lower,minimizer.get_merrors()[akey].upper])
                        apar.Error(minimizer.errors[akey])
        self.fitresult = minimizer


    def residual(self):
        return self.residuals, self.std(self.residuals)

    def params(self):
        return [k.Value() for k in self.parlist]

    def errors(self):
        return [k.Error() for k in self.parlist] 

    def stats(self):
        '''Returns a string with the fit statistics seperated with newlines'''
        statlbl = ""
        statlbl = "Chi2/N = {:.3}".format(
            self.GetChisquare() / self.GetNDof())
        # statlbl += "\nP     = {:2.2e}".format(fit.GetProb()) Make own routine
        # to calculate chiprob
        for apar in self.parlist:
            if self.assymetricalErrors:
                statlbl += "\n{} = {:.2} +- ({: .3},{: .3})".format(
                    apar.Name(), apar.Value(),apar.Error()[0],apar.Error()[1])

            else:
                statlbl += "\n{} = {: .2} +- {: .3}".format(
                    apar.Name(), apar.Value(),apar.Error())
        return statlbl


class internalParameter:
    def __init__(self, name, value, initvalue=1, bounds=(None, None),stepsize = 1):
        self.name = name
        self.value = value
        self.bounds = bounds
        self.initvalue = initvalue
        self.stepsize = stepsize
        self.ifbound = True if bounds != (None, None) else False
        self.error = 1.0

    def Name(self, name=None):
        '''Gets or sets name'''
        if not isinstance(name, (str, type(None))):
            raise TypeError('The name must be a string')
        if name is not None:
            self.name = name
        return self.name

    def Value(self, val=None):
        '''Gets or sets value'''
        if not isinstance(val, (float, int, type(None))):
            raise TypeError('The value must be a float or int')
        if val is not None:
            self.value = float(val)
        return self.value

    def Initialvalue(self, initval=None):
        '''Gets or sets the initial value'''
        if not isinstance(initval, (float, int, type(None))):
            raise TypeError('The value must be a float or int')
        if initval is not None:
            self.initvalue = float(initval)
        return self.initvalue

    def Error(self, err=None):
        '''Gets or sets error'''
        if err is not None:
            if isinstance(err, list):
                for anerr in err:
                    if not isinstance(anerr, (float, int, type(None))):
                        raise TypeError('The error must be a float or int')
                self.error = [float(err[0]),float(err[1])]    
            if not isinstance(err, (float, int, type(None))):
                raise TypeError('The error must be a float or int')
            self.error = float(err)
        return self.error

    def Ifbound(self, flag=None):
        '''Gets or sets the bool if the parameter is bounded or not'''
        if not isinstance(flag, (bool, type(None))):
            raise TypeError('The flag must be either True or False')
        if flag is not None:
            self.ifbound = flag
        return self.ifbound

    def StepSize(self, step=None):
        '''Gets or sets the bool if the parameter is bounded or not'''
        if not isinstance(step, (int,float, type(None))):
            raise TypeError('The stepsize must be either float or int')
        if step is not None:
            self.stepsize = step
        return self.stepsize

    def Bounds(self, minmax=None):
        '''Gets or sets the parameter bounds (Automatically sets the ifbound flag to True)'''
        if not isinstance(minmax, (tuple, type(None))):
            raise TypeError('The bounds must be a tuple of type (min,max)')
        if minmax is not None:
            self.bounds = minmax
            self.ifbound = True
        return self.bounds
