"""Use-Cases 'FileSysObjects.addPathToSearchPath'

Find a matching relative filepathname in upper directory
tree. 

**Example**::

  a
  |-- A.txt
  `-- b
      |-- B.txt
      `-- c
          |-- C.txt
          `-- d
              `-- D.txt


Before::

  'C.txt'

Call::

   addPathToSearchPath

After::

  'a/b/c/C.txt'

"""