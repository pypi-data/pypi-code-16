import argparse
from sys import stdin
from os.path import abspath
from os.path import expanduser


class FullPaths(argparse.Action):
    """Expands user- and relative-paths
    """
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, abspath(expanduser(values)))


def parse_args():
    """Parses the command line

    Return:
    -----
    ArgParse: An ArgsParse object with the settings for the genprimers run

    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    subparsers = parser.add_subparsers(help='sub-commands help',
                                       dest="subparser_name")

    # generate index subcommand
    indx_parser = subparsers.add_parser('index',
                                        help='create an index for a set of' +
                                        ' sequences')
    indx_parser.add_argument("fasta",
                             help="FASTA file with the sequences" +
                             "to be indexed",
                             metavar="FASTA"
                             )

    # list available sequnces subcommand
    list_parser = subparsers.add_parser('list',
                                        help='list all available sequences  ' +
                                        ' to generate primers')

    list_parser.add_argument("list_fasta",
                             help="FASTA file with the sequences",
                             metavar="FASTA"
                             )

    # generate primers subcommand
    primers_parser = subparsers.add_parser('primers',
                                           help='create a set of primers for' +
                                           ' a subset, given a universe of' +
                                           ' sequences',
                                           add_help=False)
    primers_parser.add_argument("fasta_indx",
                                help="Indexed FASTA containing all the" +
                                " sequences",
                                metavar="UNIVERSE",
                                action=FullPaths)
    primers_parser.add_argument('targets_ids',
                                help='File containing the list of' +
                                ' identifiers of' +
                                ' the target sequences (default stdin)',
                                metavar="TARGETS",
                                nargs='?',
                                type=argparse.FileType('r'),
                                default=stdin)
    primers_parser.add_argument('output_prefix',
                                help='Output prefix for the results',
                                metavar="OUTPUT")
    thermo_args = primers_parser.add_argument_group('thermodynamic arguments')
    thermo_args.add_argument('-p', '--op-temp',
                             dest='op_temp',
                             help='Operation temperature in Celsius.' +
                             ' Operation temperature is the lower' +
                             ' temperature in the PCR cycle (default 50)',
                             type=float,
                             metavar='FLOAT',
                             default=50.0)
    thermo_args.add_argument('-j', '--prim-con',
                             dest='prim_con',
                             help='Primer concentration in Molar' +
                             ' (default 2e-7)',
                             type=float,
                             metavar='FLOAT',
                             default=2e-7)
    thermo_args.add_argument('-n', '--na',
                             dest='na',
                             help='Monovalent cations concentration in Molar' +
                             ' (default 5e-3)',
                             type=float,
                             metavar='FLOAT',
                             default=5e-3)
    thermo_args.add_argument('-m', '--mg',
                             dest='mg',
                             help='Divalent cations concentration in Molar' +
                             ' (default 0)',
                             type=float,
                             metavar='FLOAT',
                             default=0)
    thermo_args.add_argument('-d', '--sdss',
                             dest='sdss',
                             help='Threshold to determine SDSS region in' +
                             ' the primers (default 0.01)',
                             type=float,
                             metavar='FLOAT',
                             default=0.01)
    fil_args = primers_parser.add_argument_group('primer filtering arguments')
    fil_args.add_argument('-k', '--min-prim-size',
                          dest='min_prim_size',
                          help='Mimimum primer size in bp (default 18)',
                          type=int,
                          metavar='INT',
                          default=18)
    fil_args.add_argument('-K', '--max-prim-size',
                          dest='max_prim_size',
                          help='Maximum primer size in bp (default 22)',
                          type=int,
                          metavar='INT',
                          default=22)
    fil_args.add_argument('-t', '--min-melt',
                          dest='min_melt',
                          help='Minimum melting temperature in Celsius' +
                          ' allowed for primers (default 60)',
                          type=float,
                          metavar='FLOAT',
                          default=60.0)
    fil_args.add_argument('-T', '--max-melt',
                          dest='max_melt',
                          help='Maximum melting temperature in Celsius ' +
                          ' allowed for primers (default 65)',
                          type=float,
                          metavar='FLOAT',
                          default=65.0)
    fil_args.add_argument('-s', '--dgss',
                          dest='dgss',
                          help='Primers with a minimum energy (dG) in' +
                          ' in kcal/mol for hairpin formation below this' +
                          ' value will be discarded (default -1.5)',
                          type=float,
                          metavar='FLOAT',
                          default=-1.5)
    fil_args.add_argument('-x', '--dghm',
                          dest='dghm',
                          help='Primers with a minimum energy (dG) in' +
                          ' kcal/mol for homodimer formation (dG) below' +
                          ' this value will be discarded (default' +
                          ' -8.5)',
                          type=float,
                          metavar='FLOAT',
                          default=-8.5)
    fil_args.add_argument('-g', '--min-gc',
                          dest='min_gc',
                          help='Minimum GC percentage for primers' +
                          ' (default 30)',
                          type=float,
                          metavar='FLOAT',
                          default=30.0)
    fil_args.add_argument('-G', '--max-gc',
                          dest='max_gc',
                          help='Maximum GC percentage for primers' +
                          ' (default 70)',
                          type=float,
                          metavar='FLOAT',
                          default=70.0)
    fil_args.add_argument('-l', '--lcc',
                          dest='lcc',
                          help='Minimum local compisition complexity' +
                          ' for the primer (default 1.0)',
                          type=float,
                          metavar='FLOAT',
                          default=1.0)
    fil_args.add_argument('-e', '--edit-distance',
                          dest='edit_distance',
                          help='Maximum number of mismatches between ' +
                          ' the primer and the target sequences (default 3)',
                          type=int,
                          metavar='INT',
                          choices=[0, 1, 2, 3],
                          default=3)
    prim_args = primers_parser.add_argument_group('primers pairs arguments')
    prim_args.add_argument('-a', '--min-amp-size',
                           dest='min_amp_size',
                           help='Mimimum amplicon size in bp for a' +
                           ' given set of primers (default 100)',
                           type=int,
                           metavar='INT',
                           default=100)
    prim_args.add_argument('-A', '--max-amp-size',
                           dest='max_amp_size',
                           help='Maximum amplicon size in bp for a' +
                           ' given set of primers (default 300)',
                           type=int,
                           metavar='INT',
                           default=300)
    prim_args.add_argument('-F', '--tragets-fraction',
                           dest='target_frac',
                           help='Minimum fraction of target sequences' +
                           ' a primer must to detect in order to be' +
                           ' considered (default 0.9)',
                           type=float,
                           metavar='FLOAT',
                           default=0.9)
    prim_args.add_argument('-X', '--ppdghm',
                           dest='ppdghm',
                           help='Primers pairs with a minimum energy (dG) in' +
                           ' kcal/mol for heterodimer formation below this' +
                           ' value will be descarded (default -8.5)',
                           type=float,
                           metavar='FLOAT',
                           default=-8.5)
    out_args = primers_parser.add_argument_group('output arguments')
    out_args.add_argument("-P", "--prefix",
                          help="Prefix to be added to the primers" +
                          " identifiers (default PB)",
                          dest="primers_prefix",
                          default="PB",
                          metavar="STRING")
    out_args.add_argument("-r", "--records",
                          help='Report up to this number of primer pairs' +
                          ' (default 10)',
                          dest="records",
                          type=int,
                          default=10,
                          metavar="INT")
    misc_args = primers_parser.add_argument_group('miscellaneous arguments')
    misc_args.add_argument("-h", "--help",
                           action="help",
                           help="Show this help message and exit")
    misc_args.add_argument("-v", "--verbose",
                           help="Control the verbose level (default 1)",
                           dest="verb_level",
                           default="1",
                           choices=[0, 1, 2])

    args = parser.parse_args()
    return args
