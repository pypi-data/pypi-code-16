import validators

# Convience checkers
def checktype(value, type_list, is_list=False):
    if is_list:
        item = []
        for v in value:
            try:
                item.append(type_list[v])
            except KeyError as err:
                if not validators.url(v):
                    #raise KeyError('{0} is not a valid URI/lookup type'.format(v)) from err
                    err.args = ('"{0}" is not a valid URI/lookup type'.format(v),)
                    raise
                item.append(v)
    else:
        try:
            item = type_list[value]
        except KeyError as err:
            if not validators.url(value):
                err.args = ('{0} is not a valid URI/lookup type'.format(value),)
                raise
            item = value
    return item

#
# Component types
#
COMPONENT_TYPES = {
    'DNA': 'http://www.biopax.org/release/biopax-level3.owl#DnaRegion',
    'RNA': 'http://www.biopax.org/release/biopax-level3.owl#RnaRegion',
    'Protein': 'http://www.biopax.org/release/biopax- level3.owl#Protein',
    'SmallMolocule': 'http://www.biopax.org/release/biopax- level3.owl#SmallMolecule',
    'Complex': 'http://www.biopax.org/release/biopax- level3.owl#Complex',
}

TOPOLOGY_TYPES = {
    'linear': 'http://identifiers.org/so/SO:0000987',
    'circular': 'http://identifiers.org/so/SO:0000988',
}

STRAND_TYPES = {
    'single-stranded': 'http://identifiers.org/so/SO:0000984',
    'double-stranded': 'http://identifiers.org/so/SO:0000985',
}

VALID_COMPONENT_TYPES = {**COMPONENT_TYPES, **TOPOLOGY_TYPES, **STRAND_TYPES}

# Of the form type: (uri, restriction)
ROLES = {
    'Promoter': 'http://identifiers.org/so/SO:0000167',
    'RBS': 'http://identifiers.org/so/SO:0000139',
    'CDS': 'http://identifiers.org/so/SO:0000316',
    'Terminator': 'http://identifiers.org/so/SO:0000141',
    'Gene': 'http://identifiers.org/so/SO:0000704',
    'Operator': 'http://identifiers.org/so/SO:0000057',
    'Engineered Gene': 'http://identifiers.org/so/SO:0000280',
    'mRNA': 'http://identifiers.org/so/SO:0000234',
    'Effector': 'http://identifiers.org/chebi/CHEBI:35224',
}

ACCESS_TYPES = {
    'public': 'http://sbols.org/v2#public',
    'private': 'http://sbols.org/v2#private',
}

ROLE_INTEGRATION_TYPES = {
    'overrideRoles': 'http://sbols.org/v2#overrideRoles',
    'mergeRoles': 'http://sbols.org/v2#mergeRoles',
}

REFINEMENT_TYPES = {
    'useRemote': 'http://sbols.org/v2#useRemote',
    'useLocal': 'http://sbols.org/v2#useLocal',
    'verifyIdentical': 'http://sbols.org/v2#verifyIdentical',
    'merge': 'http://sbols.org/v2#merge',
}

ORIENTATION_TYPES = {
    'inline': 'http://sbols.org/v2#inline',
    'reverseComplement': 'http://sbols.org/v2#reverseComplement',
}

#
# Sequence types
#
ENCODING_URI = {
    'DNA': 'http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html',
    'RNA': 'http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html',
    'Protein': 'http://www.chem.qmul.ac.uk/iupac/AminoAcid/',
    'SmallMolecule': 'http://www.opensmiles.org/opensmiles.html',
}

RESTRICTION_TYPES = {
    'precedes': 'http://sbols.org/v2#precedes',
    'sameOrientationAs': 'http://sbols.org/v2#sameOrientationAs',
    'oppositeOrientationAs': 'http://sbols.org/v2#oppositeOrientationAs',
}

#
# Model types
#
LANGUAGE_TYPES = {
    'SBML': 'http://identifiers.org/edam/format_2585',
    'CellML': 'http://identifiers.org/edam/format_3240',
    'BioPAX': 'http://identifiers.org/edam/format_3156',
}

FRAMEWORK_TYPES = {
    'Continuous': 'http://identifiers.org/biomodels.sbo/SBO:0000062',
    'Discrete': 'http://identifiers.org/biomodels.sbo/SBO:0000063',
}

DIRECTION_TYPES = {
    'in': 'http://sbols.org/v2#in',
    'out': 'http://sbols.org/v2#out',
    'inout': 'http://sbols.org/v2#inout',
    'none': 'http://sbols.org/v2#none',
}

INTERACTION_TYPES = {
    'Inhibition': 'http://identifiers.org/biomodels.sbo/SBO:0000169',
    'Stimulation': 'http://identifiers.org/biomodels.sbo/SBO:0000170',
    'Biochemical Reaction': 'http://identifiers.org/biomodels.sbo/SBO:0000176',
    'Non-Covalent Binding': 'http://identifiers.org/biomodels.sbo/SBO:0000177',
    'Degradation': 'http://identifiers.org/biomodels.sbo/SBO:0000179',
    'Genetic Production': 'http://identifiers.org/biomodels.sbo/SBO:0000589',
    'Control': 'http://identifiers.org/biomodels.sbo/SBO:0000168',
}

PARTICIPANT_TYPES = {
    'Inhibitor': 'http://identifiers.org/biomodels.sbo/SBO:0000020',
    'Inhibited': 'http://identifiers.org/biomodels.sbo/SBO:0000642',
    'Stimulator': 'http://identifiers.org/biomodels.sbo/SBO:0000459',
    'Stimulated': 'http://identifiers.org/biomodels.sbo/SBO:0000643',
    'Reactant': 'http://identifiers.org/biomodels.sbo/SBO:0000010',
    'Product': 'http://identifiers.org/biomodels.sbo/SBO:0000011',
    'Promoter': 'http://identifiers.org/biomodels.sbo/SBO:0000598',
    'Modifier': 'http://identifiers.org/biomodels.sbo/SBO:0000019',
    'Modified': 'http://identifiers.org/biomodels.sbo/SBO:0000644',
    'Template': 'http://identifiers.org/biomodels.sbo/SBO:0000645',
}
