import apt_deps.get_deps
from subprocess import check_call


class TestGetDeps(object):

    def test_finder(self):
        a = apt_deps.get_deps.DepFinder(['apt'])
        assert 'libgcc1' in a.dep_set

    def test_cli(self):
        out = check_call(['apt-deps', 'apt'])
        assert out == 0
