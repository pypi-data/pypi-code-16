# panel is a dict containing all of the data structures that define a panel
# 	Amplicons:		genomic range
# 	Exons:			genomic range
# 	Transcripts:		genomic range
# 	Depth:
#	Variants_Disease:	genomic range
#	Variants_Gene:		genomic range
#	Variants_Mutation:	genomic range
#	Filenames:		dict of all files in the panel directory with filetype as the key
#       Options:		dict of all options, including depth

# the following are only included for a design panel
#	 AllTranscripts: 	genomic range
#	 AllExons:		genomic range
#	 Excluded:		list of excluded amplicons

import os, re, pdb
from gr import Gr
from reader import Bed, Vcf, IlluminaManifest, RefFlat, Variants
from covermiexception import CoverMiException


regexps = (("Reference",        re.compile(".+?\t.+?\tchr.+?\t[+-]\t[0-9]+\t[0-9]+\t[0-9]+\t[0-9]+\t[0-9]+\t[0-9,]+\t[0-9,]+\\s*$")), #Eleven columns - refflat
           ("Depth",            re.compile("[0-9]+\\s*$")), #Single number - depth
           ("Targets",          re.compile("[a-zA-Z][a-zA-Z0-9-]*\\s*$")), #Single column - targets
           ("Targets",          re.compile("[a-zA-Z][a-zA-Z0-9-]* +[a-zA-Z0-9_]+\\s*$")), #Single column - targets
           ("Manifest",         re.compile("\\[Header\\]$")), #Manifest
           ("Variants",         re.compile(".+?\t.+?\t.+?\t[a-zA-Z0-9]+\t(null|chr[1-9XYM][0-9]?)\t(null|[0-9]+)\t(null|[0-9]+)\t(null|[+-])\t")), #Nine columns - variants
           ("Canonical",        re.compile("[a-zA-Z][a-zA-Z0-9]*\t[a-zA-Z][a-zA-Z0-9-]* +[a-zA-Z0-9_]+\\s*$")), #Two columns - canonical
           ("Canonical",        re.compile("[a-zA-Z][a-zA-Z0-9]*\t[a-zA-Z0-9_]+\\s*$")), #Two columns - canonical
           ("DesignStudio",     re.compile("chr[0-9XYM]+\t[0-9]+\t[0-9]+[\t\n]")), #Six column Bedfile - design
           ("Disease_Names",    re.compile("#Variants Disease Name Translation\\s*$")), #Disease_Names
           ("SNPs",             re.compile("chr[1-9XYM][0-9]?:[0-9]+ [ATCG\.]+>[ATCG\.]\\s*$")), #SNPs
           ("VCF",              re.compile("##fileformat=VCFv[0-9\.]+\\s*$")), #VCF
           ("Options",          re.compile("#CoverMi options\\s*$")), # CoverMi panel options
          )



def Panels(panels_path, **kwargs):
    panels = {}
    for name in os.listdir(panels_path):
        panel_path = os.path.join(panels_path, name)
        if os.path.isdir(panel_path):
            try:
                panels[name] = Panel(panel_path, **kwargs)
            except CoverMiException:
                continue
    return panels



class Panel(object):

    @classmethod
    def build(cls, **kwargs):
        panel = cls()
        for attr, value in kwargs.items():
            setattr(panel, "_"+attr, value)
        return panel


    def __init__(self, panel_path=None, verbose=False, required=()):
        self._amplicons = None
        self._offtarget = None
        self._expected = None
        self._unexpected = None
        self._transcripts = None
        self._exons = None
        self._alltranscripts = None
        self._allexons = None
        self._variants_disease = None
        self._variants_mutation = None
        self._variants_gene = None
        self._options = None

        self.panel_path = panel_path
        self._verbose = verbose
        self._refflat_verbose = verbose
        self._variants_verbose = verbose

        self.file_names = {}

        if panel_path:
            self.file_names["Panel"] = os.path.basename(panel_path)
            found = set()
            for fn in os.listdir(panel_path):
                file_path = os.path.join(panel_path, fn)
                if not os.path.isfile(file_path): continue
                file_extension = os.path.splitext(fn)[1]
                if file_extension in (".bam", ".vcf", ".bai"): continue

                with open(file_path, "rU") as f:
                    testlines = [f.readline(), f.readline()]
                
                alreadyfound = ""
                for testline in testlines:
                    testline = testline.strip()
                    for filetype, regexp in regexps:
                        if regexp.match(testline):
                            if alreadyfound != "":
                                raise CoverMiException("Not a valid CoverMi panel\nUnable to uniquely identify file {0}, matches both {1} and {2} file formats".format(filepath, filetype, alreadyfound))
                            if filetype in self.file_names:
                                raise CoverMiException("Not a valid CoverMi panel\nFiles {} and {} both match {} format".format(filepath, self.file_names[filetype], filetype))
                            alreadyfound = filetype
                            self.file_names[filetype] = fn
                    if alreadyfound:
                        break

        for attr in required:
            test = getattr(self, attr)


    @property
    def amplicons(self):
        if self._amplicons is None:
            if "Manifest" in self.file_names and "DesignStudio" in self.file_names:
                raise CoverMiException("Both Manifest and Design Studio Files found in {0}".format(self.panel_path))
            if "Manifest" not in self.file_names and "DesignStudio" not in self.file_names:
                raise CoverMiException("Unable to identify a Manifest file or a Design Studio Bedfile in {0}".format(self.panel_path))
            if "Manifest" in self.file_names:
                if self._verbose: print "Loading manifest file: {0}".format(self.file_names["Manifest"])
                manifest = IlluminaManifest(os.path.join(self.panel_path, self.file_names["Manifest"]))
                self._amplicons = Gr(manifest)
                self._offtarget = Gr(manifest.offtarget())
            elif "DesignStudio" in self._file_names:
                if self._verbose: print "Loading Design Studio amplicons bedfile: {0}".format(self.file_names["DesignStudio"])
                self._amplicons =  Gr(Bed(os.path.join(self.panel_path, self.file_names["DesignStudio"])))
        return self._amplicons


    @property
    def offtarget(self):
        if self._offtarget is None:
            amplicons = self.amplicons
        return self._offtarget


    @property
    def expected(self):
        if self._expected is None:
            self._expected = self.amplicons.combined_with(self.offtarget).merged
        return self._expected


    @property
    def unexpected(self):
        if self._unexpected is None:
            self._unexpected = self.expected.inverted
        return self._unexpected


    def common_ref_flat_checks(self):
        extra = {}
        if "Reference" not in self.file_names:
            raise CoverMiException("Unable to identify a Reference file in {0}".format(self.panel_path))
        if self._refflat_verbose: print "Loading reference file: {0}".format(self.file_names["Reference"])

        if "Canonical" in self.file_names:
            extra["canonical"] = open(os.path.join(self.panel_path, self.file_names["Canonical"]), "rb")
            if self._refflat_verbose: print "Loading canonical gene list: {0}".format(self.file_names["Canonical"])
        else:
            if self._refflat_verbose: print "WARNING. No canonical gene list found. Loading all transcripts of targeted genes"        
        self._refflat_verbose = False
        return extra


    @property
    def transcripts(self):
        if self._transcripts is None:
            extra = self.common_ref_flat_checks()

            if "Targets" in self.file_names:
                extra["genes"] = open(os.path.join(self.panel_path, self.file_names["Targets"]), "rb")
                if self._verbose: print "Loading targeted genes file: {0}".format(self.file_names["Targets"])
                if self.amplicons is None:
                    if self._verbose: print "No amplicons in panel. Will perform coverage analysis over exons of genes in targets file"

            refflatreader = RefFlat(os.path.join(self.panel_path, self.file_names["Reference"]), **extra)
            self._exons = Gr(refflatreader.read(RefFlat.EXONS))                                                     
            self._transcripts = Gr(refflatreader.read(RefFlat.TRANSCRIPTS))

            if "Targets" not in self.file_names:
                if self._verbose: print "WARNING. No file identifying targeted genes. Loading all genes touched by an amplicon"
                self._transcripts = self._transcripts.touched_by(self.amplicons) # Will raise an uncaught exception if not present, as intended
                self._exons = self._exons.touched_by(self._transcripts).subset(self._transcripts.names)
        return self._transcripts
 

    @property
    def exons(self):
        if self._exons is None:
            transcripts = self.transcripts
        return self._exons


    @property
    def alltranscripts(self):
        if self._alltranscripts is None:
            extra = self.common_ref_flat_checks()

            refflatreader = RefFlat(os.path.join(self.panel_path, self.file_names["Reference"]), **extra)
            self._allexons = Gr(refflatreader.read(RefFlat.EXONS))                                                     
            self._alltranscripts = Gr(refflatreader.read(RefFlat.TRANSCRIPTS)) 
        return self._alltranscripts
 

    @property
    def allexons(self):
        if self._allexons is None:
            alltranscripts = self.alltranscripts
        return self._allexons


    def common_variants_checks(self):
        extra = {}
        if self._variants_disease is None:
            if "Variants" not in self.file_names:
                raise CoverMiException("Unable to identify a Variants file in {0}".format(self.panel_path))
        if self._variants_verbose: print "Loading variants file: {0}".format(self.file_names["Variants"])
        if "Disease_Names" in self.file_names:
            if self._variants_verbose: print "Loading disease names file: {0}".format(self.file_names["Disease_Names"])
            extra["disease_names"] = open(os.path.join(self.panel_path, self.file_names["Disease_Names"]), "rb")
        self._variants_verbose = False    
        return extra


    @property
    def variants_disease(self):
        if self._variants_disease is None:
            extra = self.common_variants_checks()
            self._variants_disease = Gr(Variants(os.path.join(self.panel_path, self.file_names["Variants"]), **extra).read(Variants.DISEASE))        
        return self._variants_disease


    @property
    def variants_gene(self):
        if self._variants_gene is None:
            extra = self.common_variants_checks()
            self._variants_gene = Gr(Variants(os.path.join(self.panel_path, self.file_names["Variants"]), genes=self.transcripts.names, **extra).read(Variants.GENE))

            # Check to try and see if the variants file is aligned against the correct reference genome
            targeted_variants = self._variants_gene.subset(self.transcripts.names)
            variants_in_correct_location = targeted_variants.touched_by(self.transcripts).number_of_components * 100 // targeted_variants.number_of_components
            if variants_in_correct_location < 98:
                if self._verbose: print "WARNING. Only {}% of targeted variants are within targeted genes. ?Correct reference genome".format(variants_in_correct_location)
        return self._variants_gene


    @property
    def variants_mutation(self):
        if self._variants_mutation is None:
            extra = self.common_variants_checks()
            self._variants_mutation = Gr(Variants(os.path.join(self.panel_path, self.file_names["Variants"]), genes=self.transcripts.names, **extra).read(Variants.MUTATION))
        return self._variants_mutation


    @property
    def depth(self):
        try:
            return self.options["Depth"]
        except KeyError:
            raise CoverMiException("Depth not available")


    @property
    def options(self): 
        if self._options is None:
            self._options = {}
            if "Depth" in self.file_names:
                with open(os.path.join(self.panel_path, self.file_names["Depth"]), "rU") as f:
                    self._options["Depth"] = f.read().strip()
            if "Options" in self.file_names:
                if self._verbose: print "Loading options file: {0}".format(self.file_names["Options"])
                with open(os.path.join(self.panel_path, self.file_names["Options"]), "rU") as f:
                    for line in f:
                        line = line.strip()
                        if line != "" and not line.startswith("#"):
                            line = line.split("=")
                            if len(line) != 2:
                                raise CoverMiException("Malformed options file: {0}".format("=".join(line)))
                            if line[0] in self._options:
                                raise CoverMiException("Duplicate option: {0}".format(line[0]))
                            self._options[line[0]] = line[1]
            if "Depth" in self._options:
                if  not self._options["Depth"].isdigit():                
                    raise CoverMiException("Depth is not numeric: {0}".format(self._options["Depth"]))
                self._options["Depth"] = int(self._options["Depth"])
        return self._options


    def write_options(self):
        if self._options is None:
            self._options = {}
        if "Options" not in self.file_names:
            self.file_names["Options"] =  "covermi_options.txt"
            if os.path.lexists(os.path.join(self.panel_path, self.file_names["Options"])):
                raise CoverMiException("File covermi_options.txt exists but is not of correct format")
        with open(os.path.join(self.panel_path, self.file_names["Options"]), "wt") as f: 
            f.write("#CoverMi options\n")
            for key, value in self._options.items():
                f.write("{0}={1}\n".format(key, value))
        if "Depth" in self.file_names:
            os.unlink(os.path.join(self.panel_path, self.file_names["Depth"]))


    def __contains__(self, attr):
        try:
            test = getattr(self, attr)
        except CoverMiException:
            return False
        return True



if __name__ == "__main__":
    panel = Panel("/home/ed/Desktop/panels/Iron Panel v2 - 13.04.15_HD")
    print panel.variants_disease
    print panel.variants_mutation
    print panel.variants_gene
    print panel.depth
















