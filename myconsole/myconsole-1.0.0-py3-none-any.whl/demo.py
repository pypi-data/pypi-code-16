import argparse
import myconsole

BANNER =\
"""
***********************************************
*                                             *
*       Welcome to the MYCONSOLE DEMO         *
*                                             *
***********************************************
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( '--in', dest = 'inPrompt', metavar = 'STRING', default = 'MyConsole' )
    parser.add_argument( '--out', dest = 'outPrompt', metavar = 'STRING', default = None )
    arguments = parser.parse_args()
    console = myconsole.create( BANNER, arguments.inPrompt, arguments.outPrompt, exitMessage = 'enjoy your shiny new console!' )
    console()
