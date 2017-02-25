# copyright (c) 2017, Edward F. Wahl.
""" a simple preprocessor to support import into yaml files

    in a yaml file
    foo:
        bar:
            #import /home/fred/somefile.yml

    results in
    foo:
        bar:
            <contents of /home/fred/somefile.yml here, indented to the level
            of the #

    if you pass pathElements = {"user":"fred"}

    then
    foo:
        bar: #import /home/${user}/somefile.yml

    fred gets substituted for ${user}

    import occurs relative to the directory of source

    at this point there is no protection against circular imports

"""

import os
import os.path

def Run(sourcefile, pathelements = None):
    """ run
        @param source: path of file to open
        @param pathelements: map of name: path element for substitution
        """
    oldwd = os.getcwd()
    os.chdir(os.path.dirname(sourcefile))

    rv = ""
    with open(os.path.basename(sourcefile), "r") as source:
        for line in source.readlines():
            if line.lstrip().startswith("#import"):
                indent = line[:-1 * len(line.lstrip())]
                importedpath = line.split("#import")[1].strip()
                if "${" in importedpath:
                    elements = importedpath.split("${")
                    finalpath = ""
                    for element in elements:
                        if "" == element:
                            continue
                        key, rest = element.split("}")
                        finalpath += pathelements[key] + rest
                else:
                    finalpath = importedpath

                importeddata = Run(sourcefile = finalpath,
                                pathelements  = pathelements)
                for subline in importeddata.splitlines(keepends = True):
                    rv += indent + subline
                rv += "\n"

            else:
                rv += line

    os.chdir(oldwd)
    return rv
