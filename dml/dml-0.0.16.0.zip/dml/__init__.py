# Make the extended version of PyMongo available when the
# module is loaded.
from dml.dml import pymongo

# Allow users to create their own Algorithm static classes.
from dml.dml import Algorithm

# Check command line arguments and expose them when the
# module is loaded.
from dml.dml import options, auth

## eof