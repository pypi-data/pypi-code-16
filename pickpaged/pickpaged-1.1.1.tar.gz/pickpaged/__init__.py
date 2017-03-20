#-*-coding:utf-8-*-

import sys
import curses
import traceback
from pick import pick

PREV = "<< previous page" 
NEXT = ">> next page"
REFR = "<> refresh"
EXIT = "!! Exit"

def pager_options ():
    return [PREV, NEXT, REFR, EXIT]

def pickpaged (options, skip=0, limit=10, index=0, title="", indicator='*', originalSkip=0):
    """Construct and start a :class:`Picker <Picker> in a paged fashion`.

    Usage::

      >>> import pickpaged
      >>>
      >>> title = 'Please choose an option: '
      >>> skip = 0
      >>> limit = 2 # Two options per page
      >>> index = 0 # Which index to start cursor at
      >>> options = ['option1', 'option2', 'option3', 'option4', 'option5']
      >>> while True:
      >>>     options = getPage(skip, limit) # Your custom routine to get the options for the page
      >>>     option, index, skip = pickpaged.pickpaged(options, skip, limit, index, title)
      >>>     if option not in pickpaged.pager_options:
      >>>         # This is a valid option (not NEXT, PREV, REFR or EXIT)
      >>>         # Your code to work on the selected option goes here
      >>>     else:
      >>>         if option == pickpaged.EXIT:
      >>>             break
    """
    original_title = title
    try:
        optionCount = len(options)
        if optionCount == limit:
            options.append(NEXT)
        if skip > originalSkip:
            options.append(PREV)

        if skip == 0 and optionCount == 0:
            title = original_title + "\n\nNone found!"
        elif skip > 0 and optionCount == 0:
            title = original_title + "\n\nNo more found."

        options.append(REFR)
        options.append(EXIT)
        option, index = pick(options, title, indicator, index)
        if option == REFR:
            index = 0 # Reset index before redrawing current page
        elif option == NEXT:
            index = 0 # Reset index before drawing next page
            skip = skip + limit
        elif option == PREV:
            index = 0 # Reset index before drawing previous page
            skip = skip - limit
        return (option, index, skip)
    except SystemExit as e:
        sys.exit(0)
    except Exception as e:
        print(traceback.format_exc())
        sys.exit(3)
