import argparse


# https://docs.python.org/2/library/argparse.html
main = argparse.ArgumentParser(
    prog='giles',
    description=(
        'Giles is a terminal based workflow manager that integrates JIRA with '
        'both slack and github.'
    )
)

subparses = main.add_subparsers(help='help')


