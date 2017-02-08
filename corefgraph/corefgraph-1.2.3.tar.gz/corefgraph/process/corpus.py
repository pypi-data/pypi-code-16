#!/usr/bin/python
# coding=utf-8
""" This module offers the possibility of process a entire corpus of kaf files
 with corefgraph"""

import sys
import os
import re
import json
import configargparse
import codecs
import logging.config
import datetime
import collections
import logging

try:
    from corefgraph import properties
except ImportError as ie:
    sys.path.append(os.getcwd())
    from corefgraph import properties

import pycorpus
from file import generate_parser as generate_parser_for_file, process as process_file


__author__ = 'Josu Bermúdez <josu.bermudez@deusto.es>'
__created__ = '27/06/13'


# Logging
logger = logging.getLogger(__name__)

NAME_START = "result"
SPACE_CHAR = "_"
LINE_PATTERN = "{0:<20}\t{1}\t {2}\t {3}"


def generate_parser():
    """The parser used to provide configuration from experiment module to
    coreference module.

    Inherited all the properties from coreference module original parser and add
    more for handle the result store.

    :return The parser
    """
    parser = configargparse.ArgumentParser(
        parents=[generate_parser_for_file()], add_help=False)
    parser.add_argument('--result', dest='result', action='append',
                        default=["coref"],
                        help="The extension added to result files.")
    parser.add_argument('--metrics', dest='metrics', action='append',
                        default=[],
                        help="The metric of the evaluation.")
    parser.add_argument('--f1_metrics', dest='f1_metrics', action='append',
                        default=[],
                        help="The metric of the evaluation.")
    parser.add_argument('--speaker_extension', dest='speaker_extension',
                        action='store', default=None,
                        help="The extension of the speaker files(If exist).")
    parser.add_argument('--treebank_extension', dest='treebank_extension',
                        action='store', default=None,
                        help="The extension of the treebank files(If exist).")
    parser.add_argument('--evaluation_script', dest='evaluation_script',
                        action='store', default=None,
                        help="The script used in evaluation.")
    parser.add_argument('--gold', dest='golden', action='store', default=None,
                        help="The golden corpus.'")
    parser.add_argument('--result_base', dest='result_base', action='store', default=None,
                        help="CSV file with results to compare.'")
    parser.add_argument('--gold_ext', dest='golden_ext', action='store', default="conll",
                        help="The golden files extension.")
    parser.add_argument('--log_base', dest='log_base',
                        action='store', default="./log/",
                        help="The prefix of the log files")
    return parser


def file_processor(file_name, config):
    """ Extract from the base file the name of all the analysis needed for
    coreference analysis. Also if the result is in Conll format retrieve the
    part and de document name from filename.

    :param file_name: The file to bo resolved.
    :param config: The configuration for the coreference module.
    :return NOTHING
    """
    path, full_name = os.path.split(file_name)
    name, ext = os.path.splitext(full_name)
    base_name = os.path.join(path, name)

    formatter = logger.handlers[0].formatter
    file_handler = logging.FileHandler(
        filename=config.log_base + name + "." + "_".join(config.result) + "." +
        datetime.datetime.now().time().isoformat() + ".log", mode="w")
    file_handler.setFormatter(formatter)

    for logger_name in logging.Logger.manager.loggerDict:
        if logger_name.startswith("pycorpus"):
            continue
        try:
            lg = logging.Logger.manager.loggerDict[logger_name]
            for handler in lg.handlers:
                lg.removeHandler(handler)
            lg.addHandler(file_handler)
        except AttributeError:
            pass
    # Create the file names in base of original file name
    logger.info("Start processing %s", file_name)
    store_file = base_name + "." + "_".join(config.result)
    kaf_filename = base_name + ext
    logger.debug("Reading NAF from: %s", kaf_filename)
    # files
    if config.treebank_extension:
        tree_filename = base_name + config.treebank_extension
        logger.info("Using TreeBank trees: %s", tree_filename)
        try:
            trees = codecs.open(tree_filename, mode="r").read()
        except IOError as ex:
            trees = None
            logger.warning("Error in treebank file %s : %s", tree_filename, ex)
    else:
        logger.info("Using kaf trees")
        trees = None

    if config.speaker_extension:
        speaker_filename = base_name + config.speaker_extension
        try:
            speakers = codecs.open(speaker_filename, mode="r").read()
        except IOError as ex:
            logger.warning("Error in speaker file %s: %s", speaker_filename, ex)
            speakers = None
    else:
        speakers = None
        logger.debug("NO speaker file")

    # If is a Conll file add the document and part info

    config.__dict__["document_id"] = name

    # Open the files and pass the data to the module
    logger.info("Result stored in %s", store_file)
    with codecs.open(store_file, "w") as output_file:
        statistic = process_file(
            config=config,
            text=codecs.open(kaf_filename, mode="r").read(),
            parse_tree=trees,
            speakers_list=speakers,
            output=output_file
        )
    if statistic:
        with codecs.open(base_name + ".json", "w") as output_file:
            json.dump(statistic, output_file)


def evaluate(general_config, experiment_config):
    """ Evaluates all the corpus and stores the result in files

    :param general_config: The configuration applicable to all corpus
    :param experiment_config: the configuration applicable to this file.
    """
    logger.info("Evaluating: %s", experiment_config.metrics)
    path, script = os.path.split(experiment_config.evaluation_script)

    for metric in experiment_config.metrics:
        command = [
            "sh",
            script,
            os.path.abspath(experiment_config.golden),
            os.path.abspath(os.path.expanduser(general_config.directories[0])),
            "_".join(experiment_config.result),
            metric,
            experiment_config.golden_ext]
        logger.info("Metric: %s", metric)
        logger.debug("Command: %s", command)
        err, out = pycorpus.CorpusProcessor.launch_with_output(
            command, cwd=os.path.abspath(path))
        if err:
            sys.stderr.write(err)
        store_file = "{0}.{1}.{2}".format(NAME_START, "_".join(experiment_config.result),
                                          metric)
        logger.info("Evaluation stored in %s", store_file)
        with codecs.open(store_file, "w") as output_file:
            output_file.write(err)
            output_file.write(out)
    logger.info("Evaluation end.")


def report(general_config, common_config):
    """ Generate a email report of the experiment.

    :param general_config: The general config.
    :param common_config: The config used in all experiments.
    """
    logger.info("Generating report")
    logger.info("F1 : %s", common_config.f1_metrics)
    report_text = generate_report(
        path=os.path.abspath("."),
        baseline_file=common_config.result_base,
        metrics=common_config.metrics,
        f1_metrics=common_config.f1_metrics)
    print(report_text)


def generate_report(path, baseline_file=None, metrics=(), f1_metrics=()):
    """ Find any result files in path and make a report with it.

    :param path: The path of the evaluation results.
    :param baseline_file: A file that contains a csv values to compare.
    :param metrics: The metrics showed in the report.
    :param f1_metrics: The metric used to calculate de F1 value.

    :return: a list of Strings with the report.
    """
    if len(metrics) == 0:
        metrics = ["MD", "bcub", "ceafe", "ceafm", "muc"]
    if len(f1_metrics) == 0:
        f1_metrics = ("muc", "bcub", "ceafe",)
    else:
        metrics.append("conll")
    row_separator = "\n"
    column_separator = ","

    red = "\x1b[31m"
    green = "\x1b[32m"
    reset = "\x1b[0m"

    base_table = {}
    if baseline_file:
        base_table = json.load(open(baseline_file))

    file_list = [file_name for file_name in os.listdir(path) if
                 file_name.startswith(NAME_START)]
    file_list.sort()
    results = collections.defaultdict(lambda: collections.defaultdict(dict))
    for file_name in file_list:
        inside = open(file_name).readlines()
        if inside[-1].startswith("-"):
            values = re.findall(r"\d+\.?\d*%", inside[-2])
        else:
            values = re.findall(r"\d+\.?\d*%", inside[-1])

        caption = file_name.replace(SPACE_CHAR, " ").split(".")
        results[caption[1]][caption[2]] = \
            values[0][:-1], values[1][:-1], values[2][:-1]

        # this is only need to do once but doesn't harm do more(if evaluation
        # script is correct)
        if inside[-3].startswith("-"):
            values = re.findall(r"\d+\.?\d*%", inside[-4])
        else:
            values = re.findall(r"\d+\.?\d*%", inside[-2])

        results[caption[1]]["MD"] = values[0][:-1], values[1][:-1], \
            values[2][:-1]

    table = []
    # Fill the rows of the table
    for sieve in sorted(results.keys()):
        table.append(sieve)
        f1 = 0.00
        for metric in sorted(results[sieve].keys()):
            try:
                buff = []
                for x in range(len(results[sieve][metric])):
                    base = base_table[sieve][(metrics.index(metric) * 3) + x]
                    actual = float(results[sieve][metric][x])
                    if base > actual:
                        buff.append("{0}{1:5.2f}#{2:.2f}{3}".format
                                    (red, actual, abs(actual - base), reset))
                    elif base < actual:
                        buff.append(
                            "{0}{1:5.2f}#{2:.2f}{3}".format(
                                green, actual, actual - base, reset))
                    else:
                        buff.append("{0:10.2f}".format(actual))
                table.extend(buff)
            except KeyError:
                # print ex
                table.extend(["{0:9.2f}".format(float(actual)) for actual in
                              results[sieve][metric]])
            if metric in f1_metrics:
                f1 += float(results[sieve][metric][2])
        if f1_metrics:
            actual = f1 / len(f1_metrics)
            try:
                base = float(base_table[sieve][15])
            except KeyError:
                base = actual
            if actual < base:
                table.append(
                    "{0}{1:5.2f}({2:.2f}){3}".format(red, actual, actual - base,
                                                     reset))
            elif base < actual:
                table.append(
                    "{0}{1:5.2f}({2:.2f}){3}".format(green, actual, actual - base,
                                                     reset))
            else:
                table.append("{0:10.2f}".format(actual))
        table.append(row_separator)
    # Add the head of the table
    head_row = list()
    head_row.append("config".ljust(len(table[0])))
    for label in sorted(results.items()[0][1].keys()):
        head_row.extend([
            "{0:>8}_R".format(label),
            "{0:>8}_P".format(label),
            "{0:>8}_F".format(label),
        ])
    if f1_metrics:
        head_row.append("{0:>10}".format("conll_F"))
    head_row.append(row_separator)
    table = head_row + table

    return column_separator.join(table).replace(row_separator + column_separator, row_separator)


def main(filename=None):
    """ Run the corpus processing.

    :param filename: The name of the parameter file
    """
    experiment_instance = pycorpus.CorpusProcessor(
        generate_parser_function=generate_parser,
        process_file_function=file_processor,
        evaluation_script=evaluate,
        report_script=report)
    experiment_instance.run_corpus(filename)


if __name__ == "__main__":
    main()
