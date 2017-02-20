class RDFSClass(DataObjectSingleton):  # This maybe becomes a DataObject later

    """ The DataObject corresponding to rdfs:Class """
    # XXX: This class may be changed from a singleton later to facilitate dumping
    #      and reloading the object graph
    rdf_type = R.RDFS['Class']
    auto_mapped = True

    def __init__(self):
        super(RDFSClass, self).__init__(R.RDFS["Class"])

