import os
import Env
from SCLang import *
from ..ServerManager import Server
from ..Settings import SYNTHDEF_DIR

# Container for SynthDefs

class SynthDict(dict):
    module = None
    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)
    def __str__(self):
        return str(self.keys())
    def __repr__(self):
        return str(self.keys())
    def __call__(self, name):
        return self[name]
    def reload(self):
        reload(self.module)

# Create container for SynthDefs

SynthDefs = SynthDict()

# SynthDef Base Class

class SynthDefBaseClass(object):
    
    server = Server
    var = ['osc', 'env']
    defaults = {}
    container = SynthDefs
    default_env = Env.perc()

    def __init__(self, name):
        # String name of SynthDef
        self.name = name
        # Flag when Synth added to server
        self.synth_added = False
        # Initial behaviour such as amplitude / frequency modulation
        self.base = []
        self.attr = [] # stores custom attributes

        # Name of the file to store the SynthDef
        self.filename     = SYNTHDEF_DIR + "/{}.scd".format(self.name)

        # SynthDef default arguments
        self.osc         = instance("osc")
        self.freq        = instance("freq")
        self.fmod        = instance("fmod")
        self.output      = instance("output")
        self.sus         = instance("sus")
        self.amp         = instance("amp")
        self.pan         = instance("pan")
        self.rate        = instance("rate")
        self.bits        = instance("bits")
        
        self.defaults = {   "amp"       : 1,
                            "sus"       : 1,
                            "pan"       : 0,
                            "freq"      : 0,
                            "fmod"      : 0,
                            "rate"      : 1,
                            "bus"       : 0,
                            "bits"      : 0 } # This is an effect in the synthdef - bad idea?

        self.add_base_class_behaviour()

    # Context Manager
    # ---------------

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.add()

    # String representation
    # ---------------------

    def __str__(self):
        Def  = "SynthDef.new(\{},\n".format(self.name)
        Def += "{}|{}|\n".format("{", format_args(kwargs=self.defaults, delim='='))
        Def += "{}\n".format(self.get_base_class_variables())
        Def += "{}\n".format(self.get_base_class_behaviour())
        Def += "{}".format(self.get_custom_behaviour())
        # Put oscillator and envelope together, limit, pan -> out?
##        Def += "osc = Limiter.ar(osc, level: limit);\n"
        Def += "osc = osc * [min(1, (1-pan)/2), min(1, (pan+1)/2)];\n"
        Def += "\tReplaceOut.ar(bus, osc)"
        Def += "}).add;\n"
        return Def

    def __repr__(self):
        return str(self.name)

    # Combining with other SynthDefs
    # ------------------------------

    def __add__(self, other):
        if not isinstance(other, SynthDef):
            raise TypeError("Warning: '{}' is not a SynthDef".format(str(other)))
        new = copy(self)
        new.osc = self.osc + other.osc
        return new

    # Returning the SynthDefProxy
    # ---------------------------

    def __call__(self, degree=None, **kwargs):
        return SynthDefProxy(self.name, degree, kwargs)

    # Getter and setter
    # -----------------

    def __getattribute__(self, key):
        if key.startswith("_"):
            return object.__getattribute__(self, key)
        
        defaults    = object.__getattribute__(self, 'defaults')
        var         = object.__getattribute__(self, 'var')
        synth_added = object.__getattribute__(self, 'synth_added')
        attr = defaults.keys() + var
        
        if synth_added:
            return object.__getattribute__(self, key)
        elif key in attr:
            return instance(key)
        else:
            return object.__getattribute__(self, key)
        raise AttributeError("Attribute '{}' not found".format(key))

    def __setattr__(self, key, value):
        try:
            if key in self.var + self.defaults.keys():
                self.attr.append((key, value))
        except:
            pass
        if key not in self.__dict__ or str(key) != str(value):
            self.__dict__[key] = value


    # Defining class behaviour
    # ------------------------

    def add_base_class_behaviour(self):
        """ Defines the initial setup for every SynthDef """
        return

    def get_base_class_behaviour(self):
        return "\n".join(self.base)

    def get_base_class_variables(self):
        return "var {};".format(", ".join(self.var))

    def get_custom_behaviour(self):
        string = ""
        for arg, value in self.attr:
            arg, value = str(arg), str(value)
            if arg != value:
                string += (arg + '=' + value + ';\n')
        return string

    def get_custom_behaviour2(self):
        string = ""
        for arg in self.defaults.keys() + self.var:
            if arg in self.__dict__:
                # Don't add redundant lines e.g. sus=sus;
                if str(arg) != str(self.__dict__[arg]):
                    string += (str(arg) + '=' + str(self.__dict__[arg]) + ';\n')
        return string
                

    # Adding the SynthDef to the Server
    # ---------------------------------

    def write(self):
        """  Writes the SynthDef to file """
        with open(self.filename, 'w') as f:
            f.write(self.__str__())

    def has_envelope(self):
        try:
            object.__getattribute__(self, 'env')
            return True
        except:
            return False
    
    def add(self):
        """ This is required to add the SynthDef to the SuperCollider Server """

        if self.has_envelope():

            self.osc = self.osc * self.env
    
        try:
            
            # Write file
            self.write()

            self.synth_added = True

            # Load to server
            SynthDef.server.loadSynthDef(self.filename)

            # Add to list
            self.container[self.name] = self
            
        except Exception as e:
            
            WarningMsg("Error: SynthDef '{}' could not be added to the server:\n{}".format(self.name, e))

        return None

    def rename(self, newname):
        new = copy(self)
        new.name = str(newname)
        return new

    def play(self, freq, **kwargs):
        ''' Plays a single sound '''
        message = ["freq", freq]
        for key, value in kwargs.items():
            message += [key, value]
        self.server.sendNote(self.name, message)
        return

###

class SynthDef(SynthDefBaseClass):
    def __init__(self, *args, **kwargs):
        SynthDefBaseClass.__init__(self, *args, **kwargs)
        # Player Keywords
        self.vib         = instance("vib")
        self.vibDelay    = instance("vibDelay")
        self.vibVar      = instance("vibVar")
        self.depthVar    = instance("depthVar")
        self.depth       = instance("depth")
        self.slide       = instance("slide")
        self.slidefrom   = instance("slidefrom")
        # Player Default Values
        self.defaults.update( {"vib"       : 0,
                               "slide"     : 0,
                               "slidefrom" : 1 } )

    def add_base_class_behaviour(self):
        """ Defines the initial setup for every SynthDef """
        SynthDefBaseClass.add_base_class_behaviour(self)
        self.base.append("freq = freq + fmod;")
        self.base.append("freq = Line.ar(freq * slidefrom, freq * (1 + slide), sus);")
        self.base.append("freq = Vibrato.kr(freq, rate: vib);")
        return
        
class SampleSynthDef(SynthDefBaseClass):
    def __init__(self, *args, **kwargs):
        SynthDefBaseClass.__init__(self, *args, **kwargs)
        # Sample Player Keywords
        self.buf   = instance("buf")
        self.scrub = instance("scrub")
        # Sample Player Default Values
        self.defaults['buf']   = 0
        self.defaults['scrub'] = 0
        self.defaults['cut']   = 1
        
        self.base.append("Line.kr(0,1, BufDur.kr(buf) * cut * (1 / rate), doneAction: 2);")

        


'''
    SynthDefProxy Class
    -------------------

    
'''

class SynthDefProxy:
    def __init__(self, name, degree, kwargs):
        self.name = name
        self.degree = degree
        self.mod = 0
        self.kwargs = kwargs
        self.methods = {}
        self.vars = vars(self)
    def __str__(self):
        return "<SynthDef Proxy '{}'>".format(self.name)
    def __add__(self, other):
        self.mod = other
        return self
    def __coerce__(self, other):
        return None
    def __getattr__(self, name):
        if name not in self.vars:
            def func(*args, **kwargs):
                self.methods[name] = (args, kwargs)
                return self
            return func
        else:
            return getattr(self, name)
