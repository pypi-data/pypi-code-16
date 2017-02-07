"""Job output backends."""

import os

from jinja2 import Environment, PackageLoader

ENV = Environment(loader=PackageLoader('jobarchitect', 'templates'),
                  keep_trailing_newline=True)


class JobSpec(object):
    """Job specification class."""

    def __init__(self, program_template, dataset_path,
                 output_root, hash_ids, image_name=None):

        self._spec = dict()
        self._spec["program_template"] = program_template
        self._spec["dataset_path"] = os.path.abspath(dataset_path)
        self._spec["output_root"] = os.path.abspath(output_root)
        self._spec["hash_ids"] = " ".join([str(i) for i in hash_ids])
        if image_name is not None:
            self._spec["image_name"] = image_name

    def __getitem__(self, key):
        return self._spec[key]

    def keys(self):
        return self._spec.keys()

    @property
    def program_template(self):
        """Return the program template string."""
        return self._spec["program_template"]

    @property
    def dataset_path(self):
        """Return the dataset path."""
        return self._spec["dataset_path"]

    @property
    def output_root(self):
        """Return the output root path."""
        return self._spec["output_root"]

    @property
    def hash_ids(self):
        """Return the hash identifiers as a string."""
        return self._spec["hash_ids"]

    @property
    def image_name(self):
        """Return the container image name."""
        if "image_name" not in self._spec:
            raise(AttributeError("Image name not specified"))
        return self._spec["image_name"]


def generate_bash_job(jobspec):
    """Return bash job script job as a string.

    The script contains code to run all analysis on all data in one chunk from
    a split dataset.

    :param jobspec: job specification as a :class:`jobarchitect.JobSpec`
    :returns: bash job script as a string
    """
    template = ENV.get_template("bash_job.sh.j2")
    return template.render(jobspec)


def generate_docker_job(jobspec):
    """Return docker job script as a string.

    The script contains code to run a docker container to analyse data.

    :param jobspec: job specification as a :class:`jobarchitect.JobSpec`
    :returns: docker job script as a string
    """
    template = ENV.get_template("docker_job.sh.j2")
    return template.render(jobspec)


def generate_singularity_job(jobspec):
    """Return singularity job script as a string.

    The script contains code to run a docker container to analyse data.

    :param jobspec: job specification as a :class:`jobarchitect.JobSpec`
    :returns: docker job script as a string
    """
    template = ENV.get_template("singularity_job.sh.j2")
    return template.render(jobspec)


def render_script(template_name, variables):
    """Return script as a string.
    """
    template = ENV.get_template(template_name)
    return template.render(variables)
