from __future__ import print_function

from contextional import GroupContextManager as GCM


class T(object):

    def assertThing(self, arg):
        assert arg == 4


GCM.utilize_asserts(T)


with GCM("TEst") as t:

    @t.add_test("stuff")
    def test(case):
        case.assertThing(4)

    with t.add_group("other"):
        @t.add_test("stuff")
        def test(case):
            case.assertThing(2)


t.create_tests(globals())
