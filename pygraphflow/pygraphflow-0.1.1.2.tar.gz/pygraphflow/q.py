import collections

MATCH = "MATCH "
CONTINUOUS_MATCH = "CONTINUOUS MATCH "
CREATE = "CREATE "
DELETE = "DELETE "
SET = "SET "

class UDF(collections.namedtuple('UDF', ['jar_file_path', 'class_name'])):
    __slots__ = ()
    
    def __str__(self):
        return (' ON EMERGENCE ACTION UDF ' + self.class_name + ' IN ' +
                self.jar_file_path)
