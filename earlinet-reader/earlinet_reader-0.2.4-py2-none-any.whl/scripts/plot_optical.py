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

from ..optical_files import OpticalFile
from ..create_html import create_optical_html
from ..__init__ import __version__


def plot_single_file(file_path, args):
    p = read_elda_file(file_path)

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
        p.plot_data(z_min=args.zmin, z_max=args.zmax, grid=args.grid, errorevery=args.errorevery)
    output_filename = p.get_variable_plot_name('all')
    return output_filename


def plot_single_variable(args, p):
    if args.variable not in p.data_variables:
        logging.error("Variable %s not found in file. Available: %s" % (args.variable, p.data_variables))
        sys.exit(1)

    logging.debug("Plotting image file for %s variable." % args.variable)
    with warnings.catch_warnings():  # Catch warning "Converting masked element to nan"
        warnings.simplefilter("ignore")
        p.plot_data_variable(args.variable, z_min=args.zmin, z_max=args.zmax, grid=args.grid, errorevery=args.errorevery)
    output_filename = p.get_variable_plot_name(args.variable)

    return output_filename


def create_html_single_file(file_path, args):
    p = read_elda_file(file_path)

    image_dir_base = p.file_name.replace('.', '_')
    image_dir = image_dir_base + '_images'

    if not os.path.exists(image_dir):
        logging.debug("Creating directory %s that does not exist." % image_dir)
        os.makedirs(image_dir)


    logging.debug("Plotting image file for %s" % p.file_name)
    with warnings.catch_warnings():  # Catch warning "Converting masked element to nan"
       warnings.simplefilter("ignore")
       p.plot_data(z_min=args.zmin, z_max=args.zmax, grid=args.grid, errorevery=args.errorevery, add_suptitle=False)

    output_filename = p.get_variable_plot_name('all')
    output_path = os.path.join(image_dir, output_filename)
    plt.savefig(output_path, dpi=args.dpi)
    logging.debug("Plot saved.")

    create_optical_html(p, image_dir)


def read_elda_file(file_path):
    try:
        p = OpticalFile(file_path)
    except IOError:
        logging.error("Could not read file %s." % file_path)
        sys.exit(1)
    return p


def main():
    # Define the command line argument
    parser = argparse.ArgumentParser(
        description="Command line tool to plot lidar optical property files.")
    parser.add_argument("file_patter", help="The path to a file (possibly including glob patterns).")
    parser.add_argument("zmin", type=float, nargs='?', help="(optional) Minimum altitude asl to plot (in km)",
                        default=0)
    parser.add_argument("zmax", type=float, nargs='?', help="(optional) Maximum altitude asl to plot (in km)",
                        default=20)
    parser.add_argument('-v', '--variable', help="Name of variable to plot")
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
