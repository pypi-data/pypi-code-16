"""Searches for a pattern in paths from a provided list of strings.

Searches for a given path component by various constraints
on each string of provided 'plist' until the match of a break 
condition. The match is performed by default left-to-right, which 
results in top-down scan of a path hierarchy, or right-to-left as 
an upward bottom-up search.
    
Performs string operations only, the file system is neither
checked, not utilized.  
"""