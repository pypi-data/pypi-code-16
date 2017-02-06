"""jobarchitect package."""

__version__ = "0.2.0"


class JobSpec(object):
    """Job specification class."""

    def __init__(self, program_template, dataset_path,
                 output_root, hash_ids, image_name=None):

        self._spec = dict()
        self._spec["program_template"] = program_template
        self._spec["dataset_path"] = dataset_path
        self._spec["output_root"] = output_root
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
