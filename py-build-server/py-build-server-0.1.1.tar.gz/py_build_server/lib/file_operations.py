import click


class LatestTagFileParser(object):
    @staticmethod
    def is_tag_in_file(repo, tag):
        try:
            with open('/etc/py-build-server/latest-tag-{}'.format(repo.name), 'r') as file:
                data = file.read()
        except IOError:
            return False
        if data.startswith(repo.name):
            data_tag = data.split(':')[1]
            if tag == data_tag:
                print("tags match")
                return True
        return False

    @staticmethod
    def set_tag_in_file(repo, tag):
        try:
            with open('/etc/py-build-server/latest-tag-{}'.format(repo.name), 'w') as file:
                click.echo('writing to tag file')
                file.write('{}:{}'.format(repo.name, tag))
        except IOError:
            click.echo('error writing to file for repo {}'.format(repo.name))
