"""Metadata file generator module."""

class MetadataGenerator(object):
    """Metadata file generator class."""

    @staticmethod
    def generate(metadata, file_path):
        """Generates the metadata file."""
        with open(file_path, 'w') as stream:
            stream.write("\"\"\"Project metadata.\"\"\"\n")
            for key, value in metadata.items():
                if isinstance(value, list):
                    stream.write(key + " = [\n")
                    for item in value:
                        stream.write("    \"" + str(item) + "\",\n")
                    stream.write("]\n")
                else:
                    stream.write(key + " = \"" + value + "\"\n")
