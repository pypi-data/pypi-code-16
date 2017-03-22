import sys, os.path, funcy
import ruamel.yaml as yaml

from typing     import Any, Dict, Optional, List
from functools  import partial
from gaet.types import GenePattern


def is_empty_gff_file(path: str) -> bool:
    with open(path, 'r') as f:
        return all(map(lambda x: x.startswith("#") or not x.strip(), f))

def does_contain_fasta(path: str) -> bool:
    with open(path, 'r') as f:
        return any(map(lambda x: '##FASTA' in x, f))



def check_gff_file(path: Optional[str]) -> str:
    """
    Ensures the given GFF file is valid
    """
    path = str(path)
    if not os.path.isfile(path):
        err_exit('missing_file', path = path)
    if is_empty_gff_file(path):
        err_exit('empty_gff_file', path = path)
    if not does_contain_fasta(path):
        err_exit('no_fasta_entry', path = path)
    return path


def get_yaml_resource(name: str) -> Any:
    """
    Loads the contents of a package YAML file
    """
    import pkgutil
    return yaml.load(pkgutil.get_data(__name__, name + '.yml').decode('UTF-8', 'ignore'))


def get_gene_patterns() -> List[Dict[str, List[GenePattern]]]:
    import re
    f = funcy.rpartial(
            funcy.update_in,
            ['products'],
            partial(map, lambda x: GenePattern(x['name'], re.compile(x['regex']))))

    return list(map(f, get_yaml_resource('gene_types')['membership_groups']))


def err_exit(err_name: str, **args: str) -> None:
    errors = get_yaml_resource('errors')
    sys.stderr.write(errors[err_name].format(**args))
    sys.exit(1)


def parse_args(args: List[str]) -> Dict[str, Optional[str]]:
    import argparse
    parser = argparse.ArgumentParser(description = "A gene-based genome assembly evaluation tool")
    parser.add_argument('assembly', help='A GFF file containing annotations for a genome assembly.')
    parser.add_argument('--reference', '-r', required = False, help='A GFF file containing annotations for a reference genome.')
    parser.add_argument('--output',    '-o', required = False, help='Location to write generated output metrics')
    return vars(parser.parse_args(args))


def destination(args: Dict[str, Optional[str]]) -> str:
    """
    Determines the location of the output file given the parsed input args
    """
    if 'output' in args:
        return str(args['output'])
    else:
        return 'gaet_metrics.yml'

