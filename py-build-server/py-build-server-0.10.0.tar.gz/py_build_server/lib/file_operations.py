import os


class LatestTagFileParser(object):
    @staticmethod
    def is_tag_in_file(repo, tag):
        try:
            with open('/etc/py-build-server/latest-tag-{}'.format(repo.name), 'r') as file:
                data = file.read()
        except IOError:
            return False
        for line in data.splitlines():
            if line.startswith(repo.name):
                data_tag = data.split(':')[1]
                if '{}\n'.format(tag) == data_tag:
                    repo.logger.info("tags match, nothing to be done here")
                    return True
        return False

    @staticmethod
    def set_tag_in_file(repo, tag):
        try:
            with open('/etc/py-build-server/latest-tag-{}'.format(repo.name), 'w') as file:
                file.write('{}:{}\n'.format(repo.name, tag))
        except IOError:
            repo.logger.error('error writing to file for repo {}'.format(repo.name))


class BuildLogManager(object):
    def __init__(self, repo, config):
        super(BuildLogManager, self).__init__()
        self.dir = config.dir
        self.repo = repo
        repo_dirs = os.listdir(self.dir)
        if self.repo.name not in repo_dirs:
            os.mkdir('%s/%s' % (self.dir, self.repo.name), mode=0o655)

    def list_builds(self):
        return os.listdir('%s/%s' % (self.dir, self.repo.name))

    def load_build(self, commit):
        try:
            with open('%s/%s/%s' % (self.dir, self.repo.name, commit), 'r') as build:
                return build.read()
        except IOError:
            self.repo.logger.info('no build found for %s/%s' % (self.repo.name, commit))
            return False

    def save_build(self, commit, build_output, identifier=''):
        self.repo.logger.debug('writing build log file for %s/%s' % (self.repo.name, commit))
        with open('%s/%s/%s' % (self.dir, self.repo.name, commit), 'w') as build:
            build.write(build_output)
            self.repo.logger.debug('successfully wrote build log for %s/%s-%s'
                              % (self.repo.name, commit, identifier))
