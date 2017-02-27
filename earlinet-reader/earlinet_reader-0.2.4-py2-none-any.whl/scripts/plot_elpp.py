""" Command line tool to plot lidar pre-processed files from the SCC's pre-processor.
"""
import matplotlib as mpl

mpl.use('Agg')

import sys
import os
import glob
import logging
import argparse
import warnings

from matplotlib import pyplot as plt

from ..preprocessor_files import PreprocessedFile
from ..create_html import create_elpp_html
from ..__init__ import __version__


def plot_single_file(file_path, args):
    p = read_elpp_file(file_path)

    if args.variable:
        output_filename = plot_single_variable(args, p)
    else:
        output_filename = plot_all_variables(args, p)

    plt.savefig(output_filename, dpi=args.dpi)
    logging.info("Created image file %s." % output_filename)


def plot_all_variables(args, p):
    logging.debug("Plotting image file for all variable.")
    with warnings.catch_warnings():  # Catch warning "Converting masked element to nan"
        warnings.simplefilter("ignore")
        p.plot_data(r_min=args.rmin, r_max=args.rmax, v_min=args.vmin, v_max=args.vmax, grid=args.grid,
                    errorevery=args.errorevery, log=args.log, normalized=args.normalize, norm_min=args.normmin,
                    norm_max=args.normmax)
    output_filename = p.get_variable_plot_name('all')
    return output_filename


def plot_single_variable(args, p):
    if args.variable not in p.data_variables:
        logging.error("Variable %s not found in file. Available: %s" % (args.variable, p.data_variables))
        sys.exit(1)

    logging.debug("Plotting image file for %s variable." % args.variable)
    with warnings.catch_warnings():  # Catch warning "Converting masked element to nan"
        warnings.simplefilter("ignore")
        p.plot_data_variable(args.variable, r_min=args.rmin, r_max=args.rmax, v_min=args.vmin, v_max=args.vmax,
                             grid=args.grid, errorevery=args.errorevery, log=args.log, normalized=args.normalize,
                             norm_min=args.normmin, norm_max=args.normmax)
    output_filename = p.get_variable_plot_name(args.variable)

    return output_filename


def create_html_single_file(file_path, args):
    p = read_elpp_file(file_path)

    image_dir = p.file_name.replace('.nc', '_images')
    if not os.path.exists(image_dir):
        logging.debug("Creating directory %s that does not exist." % image_dir)
        os.makedirs(image_dir)

    for variable_name in p.data_variables:
        logging.debug("Plotting image file for %s variable." % variable_name)
        with warnings.catch_warnings():  # Catch warning "Converting masked element to nan"
            warnings.simplefilter("ignore")
            p.plot_data_variable(variable_name, r_min=args.rmin, r_max=args.rmax, v_min=args.vmin, v_max=args.vmax,
                                 grid=args.grid, errorevery=args.errorevery, add_suptitle=False, log=args.log,
                                 normalized=args.normalize, norm_min=args.normmin, norm_max=args.normmax)

        output_filename = p.get_variable_plot_name(variable_name)
        output_path = os.path.join(image_dir, output_filename)
        plt.savefig(output_path, dpi=args.dpi)
        logging.debug("Plot saved.")
    create_elpp_html(p, image_dir)


def read_elpp_file(file_path):
    try:
        p = PreprocessedFile(file_path)
    except IOError:
        logging.error("Could not read file %s." % file_path)
        sys.exit(1)
    return p


def main():
    # Define the command line argument
    parser = argparse.ArgumentParser(
        description="Command line tool to plot lidar pre-processed files from the SCC's ELPP.")
    parser.add_argument("file_patter", help="The path to a file (possibly including glob patterns).")
    parser.add_argument("rmin", type=float, nargs='?', help="Minimum range to plot (in km)", default=0)
    parser.add_argument("rmax", type=float, nargs='?', help="Maximum range to plot (in km)", default=20)
    parser.add_argument("--vmin", type=float, help="Minimum variable value to plot", default=None)
    parser.add_argument("--vmax", type=float, help="Maximum variable value to plot", default=None)
    parser.add_argument('-v', '--variable', help="Name of variable to plot")
    parser.add_argument('--log', help="Plot log10 values of variable.", action='store_true')
    parser.add_argument('--normalize', help="Normalize variables on molecular signal", action='store_true')
    parser.add_argument("--normmin", type=float,
                        help="If nomralize is selected, the minimum altitude for normalization (in km).", default=7)
    parser.add_argument("--normmax", type=float,
                        help="If nomralize is selected, the maximum altitude for normalization (in km).", default=9)
    parser.add_argument('--grid', help="Show grid on the plots", action='store_true')
    parser.add_argument('--dpi', type=int, help="DPI of the output image", default=150)
    parser.add_argument('--errorevery', type=int, help="Plot error bar only every x points.", default=10)
    parser.add_argument('--html', help="Create an HTML report.", action='store_true')
    # Verbosity settings from http://stackoverflow.com/a/20663028
    parser.add_argument('-d', '--debug', help="Print dubuging information.", action="store_const",
                        dest="loglevel", const=logging.DEBUG, default=logging.INFO,
                        )
    parser.add_argument('-s', '--silent', help="Show only warning and error messages.", action="store_const",
                        dest="loglevel", const=logging.WARNING
                        )
    parser.add_argument('--version', help="Show current version.", action='store_true')


    args = parser.parse_args()

    # Get the logger with the appropriate level
    logging.basicConfig(format='%(levelname)s: %(message)s', level=args.loglevel)
    logger = logging.getLogger(__name__)

    if args.version:
        print("Version: %s" % __version__)
        sys.exit(0)

    files = glob.glob(args.file_patter)

    if not files:
        logging.error("No files matching pattern %s" % args.file_patter)
        sys.exit(1)

    if args.html:
        for f in files:
            create_html_single_file(f, args)
    else:
        for f in files:
            plot_single_file(f, args)
