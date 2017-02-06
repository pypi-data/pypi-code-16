"""Tool to create jobs to carry out analyses on datasets."""

import os
import argparse

from jobarchitect import JobSpec
from jobarchitect.utils import split_dataset
from jobarchitect.backends import (
    generate_bash_job,
    generate_docker_job,
    generate_singularity_job,
    render_script,
)


def generate_jobspecs(
        program_template,
        dataset_path,
        output_root,
        nchunks,
        image_name=None
        ):
    """Return generator yielding instances of :class:`jobarchitect.JobSec`.

    :param program_template: program template string
    :param dataset_path: path to input dataset
    :param output_root: path to output root
    :param nchunks: number of chunks the job should be split into
    :param image_name: container image name
    :returns: generator yielding instances of :class:`jobarchitect.JobSec`
    """
    for file_entry_list in split_dataset(dataset_path, nchunks):
        identifiers = [entry['hash'] for entry in file_entry_list]
        yield JobSpec(
            program_template,
            dataset_path,
            output_root,
            identifiers,
            image_name=image_name
        )


class JobSketcher(object):
    """Class to build up jobs to analyse a dataset."""

    def __init__(
            self,
            program_template,
            dataset_path,
            output_root,
            image_name=None
            ):
        self.program_template = program_template
        self.dataset_path = dataset_path
        self.output_root = output_root
        self.image_name = image_name

    def _generate_jobspecs(self, nchunks):
        for jobspec in generate_jobspecs(self.program_template,
                                         self.dataset_path,
                                         self.output_root,
                                         nchunks,
                                         image_name=self.image_name):
            yield jobspec

    def sketch(self, backend, nchunks):
        """Return generator yielding instances of :class:`jobarchitect.JobSec`.

        :param backend: backend function for generating job scripts
        :param nchunks: number of chunks the job should be split into
        :returns: generator yielding jobs as strings
        """
        for jobspec in self._generate_jobspecs(nchunks):
            yield backend(jobspec)


def sketchjob(template_path, dataset_path, output_root,
              backend, nchunks, image_name=None):
    """Return list of jobs as strings.

    :param template_path: path to program template file
    :param dataset_path: path to input dataset
    :param output_root: path to output root
    :param backend: backend function for generating job scripts
    :param nchunks: number of chunks the job should be split into
    :returns: generator yielding jobs as strings
    """
    with open(template_path, "r") as fh:
        program_template = fh.read().strip()
    program_template = '"{}"'.format(program_template)
    jobsketcher = JobSketcher(
        program_template=program_template,
        dataset_path=dataset_path,
        output_root=output_root,
        image_name=image_name)
    for job in jobsketcher.sketch(backend, nchunks):
        yield job


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_description_file", help="Template describing job")
    parser.add_argument("dataset_path", help="Path to dataset to be analysed")
    parser.add_argument(
        "output_path",
        help="Path to where output will be written")
    parser.add_argument(
        "-n",
        "--nchunks",
        default=1,
        type=int,
        help="Number of chunks the job should be split up into")
    backend_function_map = {'docker': generate_docker_job,
                            'singularity': generate_singularity_job,
                            'bash': generate_bash_job}
    wrapper_script_map = {'slurm-single': "slurm_script_single.slurm.j2",
                          'slurm-multiple': "slurm_script_multiple.slurm.j2",
                          'bash': "basic_bash_script.sh.j2"}
    parser.add_argument(
        "-b",
        "--backend",
        choices=backend_function_map.keys(),
        default='bash')
    parser.add_argument(
        "-i",
        "--image-name")
    parser.add_argument(
        "-s",
        "--wrapper-script",
        choices=wrapper_script_map.keys(),
        default='bash')
    args = parser.parse_args()

    if not os.path.isfile(args.job_description_file):
        parser.error("Job description file does not exist: {}".format(
            args.job_description_file))

    if not os.path.isdir(args.dataset_path):
        parser.error("Dataset path does not exist: {}".format(
            args.dataset_path))

    if args.backend in ['docker', 'singularity']:
        if args.image_name is None:
            parser.error("""You must specify an image to use a container based
backend ({})""".format(args.backend))

    jobs = list(sketchjob(args.job_description_file,
                          args.dataset_path,
                          args.output_path,
                          backend_function_map[args.backend],
                          args.nchunks,
                          args.image_name))
    script = render_script(
        wrapper_script_map[args.wrapper_script],
        {"jobs": jobs, "partition": "rg-mh", "jobmem": 4000})
    print(script)
