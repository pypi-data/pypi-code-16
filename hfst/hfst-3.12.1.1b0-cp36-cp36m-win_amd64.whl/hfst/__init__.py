"""

Python bindings for HFST finite-state transducer library written in C++.

FUNCTIONS:

    compile_lexc_file
    compile_pmatch_expression
    compile_pmatch_file
    compile_xfst_file
    concatenate
    disjunct
    empty_fst
    epsilon_fst
    fsa
    fst
    fst_type_to_string
    get_default_fst_type
    get_output_to_console
    intersect
    is_diacritic
    read_att_input
    read_att_string
    read_att_transducer
    read_prolog_transducer
    regex
    set_default_fst_type
    set_output_to_console
    start_xfst
    tokenized_fst

CLASSES:

    AttReader
    HfstBasicTransducer
    HfstBasicTransition
    HfstInputStream
    HfstOutputStream
    HfstTokenizer
    HfstTransducer
    ImplementationType
    LexcCompiler
    PmatchContainer
    PrologReader
    XfstCompiler
    XreCompiler

"""

__version__ = "3.12.1"

import hfst.exceptions
import hfst.sfst_rules
import hfst.xerox_rules
from libhfst import is_diacritic, compile_pmatch_expression, HfstTransducer, HfstOutputStream, HfstInputStream, \
HfstTokenizer, HfstBasicTransducer, HfstBasicTransition, XreCompiler, LexcCompiler, \
XfstCompiler, set_default_fst_type, get_default_fst_type, fst_type_to_string, PmatchContainer
import libhfst

EPSILON='@_EPSILON_SYMBOL_@'
UNKNOWN='@_UNKNOWN_SYMBOL_@'
IDENTITY='@_IDENTITY_SYMBOL_@'

# Windows...
OUTPUT_TO_CONSOLE=False

def set_output_to_console(val):
    """
    (Windows-specific:) set whether output is printed to console instead of standard output.
    """
    global OUTPUT_TO_CONSOLE
    OUTPUT_TO_CONSOLE=val

def get_output_to_console():
    """
    (Windows-specific:) get whether output is printed to console instead of standard output.
    """
    return OUTPUT_TO_CONSOLE

def start_xfst(**kvargs):
    """
    Start interactive xfst compiler.

    Parameters
    ----------
    * `kvargs` :
        Arguments recognized are: type, quit_on_fail.
    * `quit_on_fail` :
        Whether the compiler exits on any error, defaults to False.
    * `type` :
        Implementation type of the compiler, defaults to
        hfst.get_default_fst_type().
    """
    import sys
    idle = 'idlelib' in sys.modules
    if idle:
        print('It seems that you are running python in in IDLE. Note that all output from xfst will be buffered.')
        print('This means that all warnings, e.g. about time-consuming operations, will be printed only after the operation is carried out.')
        print('Consider running python from shell, for example command prompt, if you wish to see output with no delays.')

    type = get_default_fst_type()
    quit_on_fail = 'OFF'
    to_console=get_output_to_console()
    for k,v in kvargs.items():
      if k == 'type':
        type = v
      elif k == 'output_to_console':
        to_console=v
      elif k == 'quit_on_fail':
        if v == True:
          quit_on_fail='ON'
      else:
        print('Warning: ignoring unknown argument %s.' % (k))

    comp = XfstCompiler(type)
    comp.setReadInteractiveTextFromStdin(True)
    comp.setReadline(False) # do not mix python and c++ readline

    if to_console and idle:
        print('Cannot output to console when running libhfst from IDLE.')
        to_console=False
    comp.setOutputToConsole(to_console)
    comp.set('quit-on-fail', quit_on_fail)

    rl_length_1 = 0
    rl_found = False
    try:
      import readline
      rl_found = True
      rl_length_1 = readline.get_current_history_length()
    except ImportError:
      pass

    import sys
    expression=""
    while True:
        expression += input(comp.get_prompt()).rstrip().lstrip()
        if len(expression) == 0:
           continue
        if expression[-1] == '\\':
           expression = expression[:-2] + '\n'
           continue
        retval = -1
        if idle:
            retval = libhfst.hfst_compile_xfst_to_string_one(comp, expression)
            stdout.write(libhfst.get_hfst_xfst_string_one())
        else:
            # interactive command
            if (expression == "apply down" or expression == "apply up") and rl_found:
               rl_length_2 = readline.get_current_history_length()
               while True:
                  try:
                     line = input().rstrip().lstrip()
                  except EOFError:
                     break
                  if expression == "apply down":
                     comp.apply_down(line)
                  elif expression == "apply up":
                     comp.apply_up(line)
               for foo in range(readline.get_current_history_length() - rl_length_2):
                  readline.remove_history_item(rl_length_2)
               retval = 0
            elif expression == "inspect" or expression == "inspect net":
               print('inspect net not supported')
               retval = 0
            else:
               retval = comp.parse_line(expression + "\n")
        if retval != 0:
           print("expression '%s' could not be parsed" % expression)
           if comp.get("quit-on-fail") == "ON":
              return
        if comp.quit_requested():
           break
        expression = ""

    if rl_found:
      for foo in range(readline.get_current_history_length() - rl_length_1):
         readline.remove_history_item(rl_length_1)

from sys import stdout

def regex(re, **kvargs):
    """
    Get a transducer as defined by regular expression *re*.

    Parameters
    ----------
    * `re` :
        The regular expression defined with Xerox transducer notation.
    * `kvargs` :
        Arguments recognized are: 'error'.
    * `error` :
        Where warnings and errors are printed. Possible values are sys.stdout,
        sys.stderr (the default), a StringIO or None, indicating a quiet mode.

    """
    type = get_default_fst_type()
    to_console=get_output_to_console()
    import sys
    err=None

    for k,v in kvargs.items():
      if k == 'output_to_console':
          to_console=v
      if k == 'error':
          err=v
      else:
        print('Warning: ignoring unknown argument %s.' % (k))

    comp = XreCompiler(type)
    comp.setOutputToConsole(to_console)

    if err == None:
       return libhfst.hfst_regex(comp, re, "")
    elif err == sys.stdout:
       return libhfst.hfst_regex(comp, re, "cout")
    elif err == sys.stderr:
       return libhfst.hfst_regex(comp, re, "cerr")
    else:
       retval = libhfst.hfst_regex(comp, re, "")
       err.write(libhfst.get_hfst_regex_error_message())
       return retval

def _replace_symbols(symbol, epsilonstr=EPSILON):
    if symbol == epsilonstr:
       return EPSILON
    if symbol == "@0@":
       return EPSILON
    symbol = symbol.replace("@_SPACE_@", " ")
    symbol = symbol.replace("@_TAB_@", "\t")
    symbol = symbol.replace("@_COLON_@", ":")
    return symbol

def _parse_att_line(line, fsm, epsilonstr=EPSILON):
    # get rid of extra whitespace
    line = line.replace('\t',' ')
    line = " ".join(line.split())
    fields = line.split(' ')
    try:
        if len(fields) == 1:
           if fields[0] == '': # empty transducer...
               return True
           fsm.add_state(int(fields[0]))
           fsm.set_final_weight(int(fields[0]), 0)
        elif len(fields) == 2:
           fsm.add_state(int(fields[0]))
           fsm.set_final_weight(int(fields[0]), float(fields[1]))
        elif len(fields) == 4:
           fsm.add_transition(int(fields[0]), int(fields[1]), _replace_symbols(fields[2]), _replace_symbols(fields[3]), 0)
        elif len(fields) == 5:
           fsm.add_transition(int(fields[0]), int(fields[1]), _replace_symbols(fields[2]), _replace_symbols(fields[3]), float(fields[4]))
        else:
           return False
    except ValueError as e:
        return False
    return True

def read_att_string(att):
    """
    Create a transducer as defined in AT&T format in *att*.
    """
    linecount = 0
    fsm = HfstBasicTransducer()
    lines = att.split('\n')
    for line in lines:
        linecount = linecount + 1
        if not _parse_att_line(line, fsm):
           raise hfst.exceptions.NotValidAttFormatException(line, "", linecount)
    return HfstTransducer(fsm, get_default_fst_type())

def read_att_input():
    """
    Create a transducer as defined in AT&T format in user input.
    An empty line signals the end of input.
    """
    linecount = 0
    fsm = HfstBasicTransducer()
    while True:
        line = input().rstrip()
        if line == "":
           break
        linecount = linecount + 1
        if not _parse_att_line(line, fsm):
           raise hfst.exceptions.NotValidAttFormatException(line, "", linecount)
    return HfstTransducer(fsm, get_default_fst_type())

def read_att_transducer(f, epsilonstr=EPSILON, linecount=[0]):
    """
    Create a transducer as defined in AT&T format in file *f*. *epsilonstr*
    defines how epsilons are represented. *linecount* keeps track of the current
    line in the file.
    """
    linecount_ = 0
    fsm = HfstBasicTransducer()
    while True:
        line = f.readline()
        if line == "":
           if linecount_ == 0:
              raise hfst.exceptions.EndOfStreamException("","",0)
           else:
              linecount_ = linecount_ + 1
              break
        linecount_ = linecount_ + 1
        if line[0] == '-':
           break
        if not _parse_att_line(line, fsm, epsilonstr):
           raise hfst.exceptions.NotValidAttFormatException(line, "", linecount[0] + linecount_)
    linecount[0] = linecount[0] + linecount_
    return HfstTransducer(fsm, get_default_fst_type())

class AttReader:
      """
      A class for reading input in AT&T text format and converting it into
      transducer(s).

      An example that reads AT&T input from file 'testfile.att' where epsilon is
      represented as \"<eps>\" and creates the corresponding transducers and prints
      them. If the input cannot be parsed, a message showing the invalid line in AT&T
      input is printed and reading is stopped.

      with open('testfile.att', 'r') as f:
           try:
                r = hfst.AttReader(f, \"<eps>\")
                for tr in r:
                    print(tr)
           except hfst.exceptions.NotValidAttFormatException as e:
                print(e.what())
      """
      def __init__(self, f, epsilonstr=EPSILON):
          """
          Create an AttReader that reads input from file *f* where the epsilon is
          represented as *epsilonstr*.

          Parameters
          ----------
          * `f` :
              A python file.
          * `epsilonstr` :
              How epsilon is represented in the file. By default, \"@_EPSILON_SYMBOL_@\"
              and \"@0@\" are both recognized.
          """
          self.file = f
          self.epsilonstr = epsilonstr
          self.linecount = [0]

      def read(self):
          """
          Read next transducer.

          Read next transducer description in AT&T format and return a corresponding
          transducer.

          Exceptions
          ----------
          * `hfst.exceptions.NotValidAttFormatException` :
          * `hfst.exceptions.EndOfStreamException` :
          """
          return read_att_transducer(self.file, self.epsilonstr, self.linecount)

      def __iter__(self):
          """
          An iterator to the reader.

          Needed for 'for ... in' statement.

          for transducer in att_reader:
              print(transducer)
          """
          return self

      def next(self):
          """
          Return next element (for python version 3).

          Needed for 'for ... in' statement.

          for transducer in att_reader:
              print(transducer)

          Exceptions
          ----------
          * `StopIteration` :
          """
          try:
             return self.read()
          except hfst.exceptions.EndOfStreamException as e:
             raise StopIteration

      def __next__(self):
          """
          Return next element (for python version 2).

          Needed for 'for ... in' statement.

          for transducer in att_reader:
              print(transducer)

          Exceptions
          ----------
          * `StopIteration` :
          """
          return self.next()

def read_prolog_transducer(f, linecount=[0]):
    """
    Create a transducer as defined in prolog format in file *f*. *linecount*
    keeps track of the current line in the file.
    """
    linecount_ = 0
    fsm = HfstBasicTransducer()
    
    line = ""
    while(True):
        line = f.readline()
        linecount_ = linecount_ + 1
        if line == "":
            raise hfst.exceptions.EndOfStreamException("","",linecount[0] + linecount_)
        line = line.rstrip()
        if line == "":
            pass # allow extra prolog separator(s)
        if line[0] == '#':
            pass # comment line
        else:
            break

    if not libhfst.parse_prolog_network_line(line, fsm):
        raise hfst.exceptions.NotValidPrologFormatException(line,"",linecount[0] + linecount_)

    while(True):
        line = f.readline()
        if (line == ""):
            retval = HfstTransducer(fsm, get_default_fst_type())
            retval.set_name(fsm.name)
            linecount[0] = linecount[0] + linecount_
            return retval
        line = line.rstrip()
        linecount_ = linecount_ + 1
        if line == "":  # prolog separator
            retval = HfstTransducer(fsm, get_default_fst_type())
            retval.set_name(fsm.name)
            linecount[0] = linecount[0] + linecount_
            return retval
        if libhfst.parse_prolog_arc_line(line, fsm):
            pass
        elif libhfst.parse_prolog_final_line(line, fsm):
            pass
        elif libhfst.parse_prolog_symbol_line(line, fsm):
            pass
        else:
            raise hfst.exceptions.NotValidPrologFormatException(line,"",linecount[0] + linecount_)

class PrologReader:
      """
      A class for reading input in prolog text format and converting it into
      transducer(s).

      An example that reads prolog input from file 'testfile.prolog' and creates the
      corresponding transducers and prints them. If the input cannot be parsed, a
      message showing the invalid line in prolog input is printed and reading is
      stopped.

          with open('testfile.prolog', 'r') as f:
              try:
                 r = hfst.PrologReader(f)
                 for tr in r:
                     print(tr)
              except hfst.exceptions.NotValidPrologFormatException as e:
                  print(e.what())
      """
      def __init__(self, f):
          """
          Create a PrologReader that reads input from file *f*.

          Parameters
          ----------
          * `f` :
              A python file.
          """
          self.file = f
          self.linecount = [0]

      def read(self):
          """

          Read next transducer.

          Read next transducer description in prolog format and return a corresponding
          transducer.

          Exceptions
          ----------
          * `hfst.exceptions.NotValidPrologFormatException` :
          * `hfst.exceptions.EndOfStreamException` :
          """
          return read_prolog_transducer(self.file, self.linecount)

      def __iter__(self):
          """
          An iterator to the reader.

          Needed for 'for ... in' statement.

          for transducer in prolog_reader:
              print(transducer)
          """
          return self

      def next(self):
          """
          Return next element (for python version 2).

          Needed for 'for ... in' statement.

          for transducer in prolog_reader:
              print(transducer)

          Exceptions
          ----------
          * `StopIteration` :
          """
          try:
             return self.read()
          except hfst.exceptions.EndOfStreamException as e:
             raise StopIteration

      def __next__(self):
          """
          Return next element (for python version 2).

          Needed for 'for ... in' statement.

          for transducer in prolog_reader:
              print(transducer)

          Exceptions
          ----------
          * `StopIteration` :
          """
          return self.next()

def compile_xfst_file(filename, **kvargs):
    """
    Compile (run) xfst file *filename*.

    Parameters
    ----------
    * `filename` :
        The name of the xfst file.
    * `kvargs` :
        Arguments recognized are: verbosity, quit_on_fail, output, type.
    * `verbosity` :
        The verbosity of the compiler, defaults to 0 (silent). Possible values are:
        0, 1, 2.
    * `quit_on_fail` :
        Whether the script is exited on any error, defaults to True.
    * `output` :
        Where output is printed. Possible values are sys.stdout, sys.stderr, a
        StringIO, sys.stderr being the default?
    * `type` :
        Implementation type of the compiler, defaults to
        hfst.get_default_fst_type().

    Returns
    -------
    On success 0, else an integer greater than 0.
    """
    verbosity=0
    quit_on_fail='ON'
    type = get_default_fst_type()
    output=None
    error=None
    to_console=get_output_to_console()

    for k,v in kvargs.items():
      if k == 'verbosity':
        verbosity=v
      elif k == 'quit_on_fail':
        if v == False:
          quit_on_fail='OFF'
      elif k == 'output':
          output=v
      elif k == 'error':
          error=v
      elif k == 'output_to_console':
          to_console=v
      else:
        print('Warning: ignoring unknown argument %s.' % (k))

    if verbosity > 1:
      print('Compiling with %s implementation...' % fst_type_to_string(type))
    xfstcomp = XfstCompiler(type)
    xfstcomp.setOutputToConsole(to_console)
    xfstcomp.setVerbosity(verbosity > 0)
    xfstcomp.set('quit-on-fail', quit_on_fail)
    if verbosity > 1:
      print('Opening xfst file %s...' % filename)
    f = open(filename, 'r', encoding='utf-8')
    data = f.read()
    f.close()
    if verbosity > 1:
      print('File closed...')

    retval=-1
    import sys
    from io import StringIO

    # check special case
    if isinstance(output, StringIO) and isinstance(error, StringIO) and output == error:
       retval = libhfst.hfst_compile_xfst_to_string_one(xfstcomp, data)
       output.write(libhfst.get_hfst_xfst_string_one())
    else:
       arg1 = ""
       arg2 = ""
       if output == None or output == sys.stdout:
          arg1 = "cout"
       if output == sys.stderr:
          arg1 == "cerr"
       if error == None or error == sys.stderr:
          arg2 = "cerr"
       if error == sys.stdout:
          arg2 == "cout"

       retval = hfst_compile_xfst(xfstcomp, data, arg1, arg2)

       if isinstance(output, StringIO):
          output.write(libhfst.get_hfst_xfst_string_one())
       if isinstance(error, StringIO):
          error.write(libhfst.get_hfst_xfst_string_two())

    if verbosity > 1:
      print('Parsed file with return value %i (0 indicating succesful parsing).' % retval)
    return retval

def compile_pmatch_file(filename):
    """
    Compile pmatch expressions as defined in *filename* and return a tuple of
    transducers.

    An example:

    If we have a file named streets.txt that contains:

    define CapWord UppercaseAlpha Alpha* ; define StreetWordFr [{avenue} |
    {boulevard} | {rue}] ; define DeFr [ [{de} | {du} | {des} | {de la}] Whitespace
    ] | [{d'} | {l'}] ; define StreetFr StreetWordFr (Whitespace DeFr) CapWord+ ;
    regex StreetFr EndTag(FrenchStreetName) ;

    we can run:

    defs = hfst.compile_pmatch_file('streets.txt')
    const = hfst.PmatchContainer(defs)
    assert cont.match("Je marche seul dans l'avenue desTernes.") ==
      "Je marche seul dans l'<FrenchStreetName>avenue des Ternes</FrenchStreetName>."
    """
    with open(filename, 'r') as myfile:
      data=myfile.read()
      myfile.close()
    defs = compile_pmatch_expression(data)
    return defs

def compile_lexc_file(filename, **kvargs):
    """
    Compile lexc file *filename* into a transducer.

    Parameters
    ----------
    * `filename` :
        The name of the lexc file.
    * `kvargs` :
        Arguments recognized are: verbosity, with_flags, output.
    * `verbosity` :
        The verbosity of the compiler, defaults to 0 (silent). Possible values are:
        0, 1, 2.
    * `with_flags` :
        Whether lexc flags are used when compiling, defaults to False.
    * `output` :
        Where output is printed. Possible values are sys.stdout, sys.stderr, a
        StringIO, sys.stderr being the default

    Returns
    -------
    On success the resulting transducer, else None.
    """
    verbosity=0
    withflags=False
    alignstrings=False
    type = get_default_fst_type()
    output=None
    to_console=get_output_to_console()

    for k,v in kvargs.items():
      if k == 'verbosity':
        verbosity=v
      elif k == 'with_flags':
        if v == True:
          withflags = v
      elif k == 'align_strings':
          alignstrings = v
      elif k == 'output':
          output=v
      elif k == 'output_to_console':
          to_console=v
      else:
        print('Warning: ignoring unknown argument %s.' % (k))

    lexccomp = LexcCompiler(type, withflags, alignstrings)
    lexccomp.setVerbosity(verbosity)
    lexccomp.setOutputToConsole(to_console)

    retval=-1
    import sys
    if output == None:
       retval = libhfst.hfst_compile_lexc(lexccomp, filename, "")
    elif output == sys.stdout:
       retval = libhfst.hfst_compile_lexc(lexccomp, filename, "cout")
    elif output == sys.stderr:
       retval = libhfst.hfst_compile_lexc(lexccomp, filename, "cerr")
    else:
       retval = libhfst.hfst_compile_lexc(lexccomp, filename, "")
       output.write(libhfst.get_hfst_lexc_output())

    return retval

def _is_weighted_word(arg):
    if isinstance(arg, tuple) and len(arg) == 2 and isinstance(arg[0], str) and isinstance(arg[1], (int, float)):
       return True
    return False

def _check_word(arg):
    if len(arg) == 0:
       raise RuntimeError('Empty word.')
    return arg

def fsa(arg):
    """
    Get a transducer (automaton in this case) that recognizes one or more paths.

    Parameters
    ----------
    * `arg` :
        See example below

    Possible inputs:

      One unweighted identity path:
        'foo'  ->  [f o o]

      Weighted path: a tuple of string and number, e.g.
        ('foo',1.4)
        ('bar',-3)
        ('baz',0)

      Several paths: a list or a tuple of paths and/or weighted paths, e.g.
        ['foo', 'bar']
        ('foo', ('bar',5.0))
        ('foo', ('bar',5.0), 'baz', 'Foo', ('Bar',2.4))
        [('foo',-1), ('bar',0), ('baz',3.5)]

    """
    deftok = HfstTokenizer()
    retval = HfstBasicTransducer()
    if isinstance(arg, str):
       retval.disjunct(deftok.tokenize(_check_word(arg)), 0)
    elif _is_weighted_word(arg):
       retval.disjunct(deftok.tokenize(_check_word(arg[0])), arg[1])
    elif isinstance(arg, tuple) or isinstance(arg, list):
       for word in arg:
           if _is_weighted_word(word):
              retval.disjunct(deftok.tokenize(_check_word(word[0])), word[1])
           elif isinstance(word, str):
              retval.disjunct(deftok.tokenize(_check_word(word)), 0)
           else:
              raise RuntimeError('Tuple/list element not a string or tuple of string and weight.')
    else:
       raise RuntimeError('Not a string or tuple/list of strings.')
    return HfstTransducer(retval, get_default_fst_type())

def fst(arg):
    """
    Get a transducer that recognizes one or more paths.

    Parameters
    ----------
    * `arg` :
        See example below

    Possible inputs:

      One unweighted identity path:
        'foo'  ->  [f o o]

      Weighted path: a tuple of string and number, e.g.
        ('foo',1.4)
        ('bar',-3)
        ('baz',0)

      Several paths: a list or a tuple of paths and/or weighted paths, e.g.
        ['foo', 'bar']
        ('foo', ('bar',5.0))
        ('foo', ('bar',5.0), 'baz', 'Foo', ('Bar',2.4))
        [('foo',-1), ('bar',0), ('baz',3.5)]

      A dictionary mapping strings to any of the above cases:
        {'foo':'foo', 'bar':('foo',1.4), 'baz':(('foo',-1),'BAZ')}
    """
    if isinstance(arg, dict):
       retval = regex('[0-0]') # empty transducer
       for input, output in arg.items():
           if not isinstance(input, str):
              raise RuntimeError('Key not a string.')
           left = fsa(input)
           right = 0
           if isinstance(output, str):
              right = fsa(output)
           elif isinstance(output, list) or isinstance(output, tuple):
              right = fsa(output)
           else:
              raise RuntimeError('Value not a string or tuple/list of strings.')
           left.cross_product(right)
           retval.disjunct(left)
       return retval
    return fsa(arg)

def tokenized_fst(arg, weight=0):
    """
    Get a transducer that recognizes the concatenation of symbols or symbol pairs in
    *arg*.

    Parameters
    ----------
    * `arg` :
        The symbols or symbol pairs that form the path to be recognized.

    Example

       import hfst
       tok = hfst.HfstTokenizer()
       tok.add_multichar_symbol('foo')
       tok.add_multichar_symbol('bar')
       tr = hfst.tokenized_fst(tok.tokenize('foobar', 'foobaz'))

    will create the transducer [foo:foo bar:b 0:a 0:z].
    """
    retval = HfstBasicTransducer()
    state = 0
    if isinstance(arg, list) or isinstance(arg, tuple):
       for token in arg:
           if isinstance(token, str):
              new_state = retval.add_state()
              retval.add_transition(state, new_state, token, token, 0)
              state = new_state
           elif isinstance(token, list) or isinstance(token, tuple):
              if len(token) == 2:
                 new_state = retval.add_state()
                 retval.add_transition(state, new_state, token[0], token[1], 0)
                 state = new_state
              elif len(token) == 1:
                 new_state = retval.add_state()
                 retval.add_transition(state, new_state, token, token, 0)
                 state = new_state
              else:
                 raise RuntimeError('Symbol or symbol pair must be given.')
       retval.set_final_weight(state, weight)
       return HfstTransducer(retval, get_default_fst_type())
    else:
       raise RuntimeError('Argument must be a list or a tuple')

def empty_fst():
    """
    Get an empty transducer.

    Empty transducer has one state that is not final, i.e. it does not recognize any
    string.
    """
    return regex('[0-0]')

def epsilon_fst(weight=0):
    """
    Get an epsilon transducer.

    Parameters
    ----------
    * `weight` :
        The weight of the final state. Epsilon transducer has one state that is
        final (with final weight *weight*), i.e. it recognizes the empty string.
    """
    return regex('[0]::' + str(weight))

def concatenate(transducers):
    """
    Return a concatenation of *transducers*.
    """
    retval = epsilon_fst()
    for tr in transducers:
      retval.concatenate(tr)
    retval.minimize()
    return retval

def disjunct(transducers):
    """
    Return a disjunction of *transducers*.
    """
    retval = empty_fst()
    for tr in transducers:
      retval.disjunct(tr)
    retval.minimize()
    return retval

def intersect(transducers):
    """
    Return an intersection of *transducers*.
    """
    retval = None
    for tr in transducers:
      if retval == None:
        retval = HfstTransducer(tr)
      else:
        retval.intersect(tr)
    retval.minimize()
    return retval

class ImplementationType:
    """
    Back-end implementation.

    Attributes:

        SFST_TYPE:               SFST type, unweighted
        TROPICAL_OPENFST_TYPE:   OpenFst type with tropical weights
        LOG_OPENFST_TYPE:        OpenFst type with logarithmic weights (limited support)
        FOMA_TYPE:               FOMA type, unweighted
        XFSM_TYPE:               XFST type, unweighted (limited support)
        HFST_OL_TYPE:            HFST optimized-lookup type, unweighted
        HFST_OLW_TYPE:           HFST optimized-lookup type, weighted
        HFST2_TYPE:              HFST version 2 legacy type
        UNSPECIFIED_TYPE:        type not specified
        ERROR_TYPE:              (something went wrong)

    """
    SFST_TYPE = libhfst.SFST_TYPE
    TROPICAL_OPENFST_TYPE = libhfst.TROPICAL_OPENFST_TYPE    
    LOG_OPENFST_TYPE = libhfst.LOG_OPENFST_TYPE
    FOMA_TYPE = libhfst.FOMA_TYPE
    XFSM_TYPE = libhfst.XFSM_TYPE
    HFST_OL_TYPE = libhfst.HFST_OL_TYPE
    HFST_OLW_TYPE = libhfst.HFST_OLW_TYPE
    HFST2_TYPE = libhfst.HFST2_TYPE
    UNSPECIFIED_TYPE = libhfst.UNSPECIFIED_TYPE
    ERROR_TYPE = libhfst.ERROR_TYPE

