"""
Export functionality for zookeeper.  Some zookeeper nodes cannot be exported directly to a file
system because they allow illegal characters. 
"""

def recursive_znode_discovery(node='/', exclude_ephemeral=True):
    