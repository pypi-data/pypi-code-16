from fabric.api import local


class LocalGitWrapper(object):
    """
    The LocalGitWrapper object is a wrapper for commond git functions to run them locally on the machine

    """

    HEAD = 'HEAD'

    @staticmethod
    def get_branch_hash(branch):
        """
        Get the branch hash of given branch name

        :return:
        """
        return local('git rev-parse --verify {}'.format(branch), capture=True)

    @staticmethod
    def create_git_archive_of_branch(branch_hash, source_path):
        """
        Creates a git archive (tar.gz) in the source path

        :param branch_hash:
        :param source_path:
        :return:
        """
        local(
            'git archive {branch_hash} --format tar.gz -o {source_path}'.format(
                branch_hash=branch_hash,
                source_path=source_path,
            )
        )

    @staticmethod
    def remove_git_archive_of_branch(source_path):
        """
        Removes a git archive (or a file)

        :param source_path:
        :return:
        """
        local(
            'rm -rf {}'.format(source_path)
        )

    @staticmethod
    def get_differ_git_commit_messages(previous_commit_hash, next_commit_hash):
        """
        Gets the commit messages between two commits

        :param previous_commit_hash:
        :param next_commit_hash:
        :return:
        """
        return local("git log {}..{}".format(previous_commit_hash, next_commit_hash), capture=True)
