from __future__ import print_function
# top comment
import os # lateral comment

# before decorator comment
@decoratortest(a = "blabla", b = 42) # decorator trailing
# before func comment
def polompos(c=69): # func lateral comment
    # comment above docstring
    """
    Docstring
    :return:
    """
    # comment below docstring # other comment # other # other
    print(os.name) # funccall lateral comment
        # comment below print indented


    if True: # if lateral comment
        # comment below if
        print('hola mundo', file=3) # xxx lateral

    for i in range(10):    
         # comment to mark whitespace checks
         print('y eso')     
    jolompos   = 2; pokorcios = 4


# after func comment

# before call comment
polompos() # funccall2 lateral comment
# finishing comment


	
# more finishing, 3 newlines before
