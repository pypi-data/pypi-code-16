class Read:
    '''
    A copy of the arguments from a AlignedSegment object relevant to this analysis.
    '''
    def __init__(self, pysam_read):
        self.reference_name = pysam_read.reference_name
        self.reference_start = pysam_read.reference_start
        self.reference_end = pysam_read.reference_end
        self.MD = pysam_read.get_tag("MD")
        self.query_name = pysam_read.query_name
        self.query_alignment_length = pysam_read.query_alignment_length
        self.query_alignment_qualities = pysam_read.query_alignment_qualities
        
    def get_tag(self, tag):
        '''Fetch the desired tag'''
        if tag == "MD":
            return self.MD
        print("Tag does not exist")
        assert False