from docker_buildtool import docker_build, dockerfile, error

class Builder(object):
    def __init__(self, dockerfile, image, variables=None, no_fetch=True, default_build_root=None, quiet=False):
        self.dockerfile = dockerfile
        self.image = image
        self.no_fetch = no_fetch

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
        self.default_build_root = default_build_root
        self.quiet = quiet

        self.spec = self.prepare()

    def prepare(self):
        return dockerfile.DockerfileBuildSpec(self.dockerfile)

    def run(self, dryrun):
        build = docker_build.DockerBuild(
            dockerfile=self.spec.dockerfile,
            build_root=self.spec.build_root or self.default_build_root,
            include=self.spec.include,
            workdir=self.spec.workdir,
            ignore=self.spec.ignore,
            docker_repo=self.docker_repo,
            tag=self.tag,
            default_ignore=self.spec.default_ignore,
            include_version_file=self.spec.include_version_file,
            variables=self.variables,
            no_fetch=self.no_fetch,
            no_ignore_override=self.spec.no_ignore_override,
            quiet=self.quiet,
        )
        build.run(dryrun=dryrun)
