""".gitignore file generator module."""

GITIGNORE_TEMPLATE = """
# Sublime project files
*.sublime-project
*.sublime-workspace

# Jetbrains IDE files
.idea/

# Virtual environments
.env
.venv

__pycache__*

# Compiled python modules.
*.pyc

# Setuptools distribution folder.
/dist/

# Python egg metadata, regenerated from source files by setuptools.
*.egg-info
*.egg
*.eggs

/build/

# Tox files
.tox/

# Coverage
.coverage
htmlcov/
cover/
"""

class GitignoreGenerator(object):
    """.gitignore file generator class."""

    @staticmethod
    def generate(file_path):
        with open(file_path, 'w') as stream:
            stream.write(GITIGNORE_TEMPLATE)