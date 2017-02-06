"""Jobarchitect agent."""

import argparse
import subprocess

from jobarchitect.utils import path_from_hash, output_path_from_hash


class Agent(object):
    """Class to create commands to analyse data."""

    def __init__(self, program_template, dataset_path, output_root="/tmp"):
        self.program_template = program_template
        self.dataset_path = dataset_path
        self.output_root = output_root

    def create_command(self, hash_str):
        """Return the command to run as a string.

        :param hash_str: dataset item identifier as a hash string
        :returns: command as a string
        """
        input_file = path_from_hash(self.dataset_path, hash_str)
        output_file = output_path_from_hash(
            self.dataset_path, hash_str, self.output_root)
        return self.program_template.format(
            input_file=input_file,
            output_file=output_file)

    def run_analysis(self, hash_str):
        """Run the analysis on an item in the dataset.

        :param hash_str: dataset item identifier as a hash string
        """
        command = self.create_command(hash_str)
        subprocess.call(command, shell=True)


def analyse_by_identifiers(
        program_template, dataset_path, output_root, identifiers):
    """Run analysis on identifiers.

    :param program_template: program template string
    :param dataset_path: path to input dataset
    :param output_root: path to output root
    :identifiers: list of identifiers
    """
    agent = Agent(program_template, dataset_path, output_root)
    for i in identifiers:
        agent.run_analysis(i)


def cli():
    """Command line interface for _analyse_by_ids"""

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--program_template', required=True)
    parser.add_argument('--input_dataset_path', required=True)
    parser.add_argument('--output_root', required=True)
    parser.add_argument('identifiers', nargs=argparse.REMAINDER)

    args = parser.parse_args()

    analyse_by_identifiers(
        args.program_template,
        args.input_dataset_path,
        args.output_root,
        args.identifiers)
