from docker_buildtool import docker_build, dockerfile, error

class Builder(object):
    def __init__(self, dockerfile, image, variables=None):
        self.dockerfile = dockerfile
        self.image = image

        if self.image is None:
            docker_repo = None
            tag = None
        else:
            parsed_tag = self.image.split(':')
            if len(parsed_tag) > 1:
                docker_repo = parsed_tag[0]
                tag = parsed_tag[1]
            else:
                docker_repo = parsed_tag[0]
                tag = 'latest'

        self.docker_repo = docker_repo
        self.tag = tag

        if variables is None:
            variables = {}
        self.variables = variables

        self.spec = self.prepare()

    def prepare(self):
        spec = dockerfile.DockerfileBuildSpec(self.dockerfile)
        if spec.frontmatter is None:
            raise error.Error("""Your Dockerfile has no frontmatter, meaning the entire build context would be ignored. That is, you would not have access to any of the files on local disk.

To fix this, add something like this to the head of your Dockerfile:

# ---
# setup: pip install -e .
# build_root: ../..
# ignore:
#  - gym-vnc-envs/vnc-flashgames/out
#  - gym-vnc/go-vncdriver
# include:
#  - gym-vnc-envs/vnc-flashgames
#  - {'path': 'gym-vnc', 'git': 'git@github.com:openai/gym-vnc.git', 'setup': 'pip install -e .'}
# ---""")
        return spec

    def run(self, dryrun):
        build = docker_build.DockerBuild(
            dockerfile=self.spec.dockerfile,
            build_root=self.spec.build_root,
            include=self.spec.include,
            workdir=self.spec.workdir,
            ignore=self.spec.ignore,
            docker_repo=self.docker_repo,
            tag=self.tag,
            default_ignore=self.spec.default_ignore,
            include_version_file=self.spec.include_version_file,
            variables=self.variables,
        )
        build.run(dryrun=dryrun)
