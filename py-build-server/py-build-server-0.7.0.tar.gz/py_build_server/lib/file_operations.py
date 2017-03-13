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
