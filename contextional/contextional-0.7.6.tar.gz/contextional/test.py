from __future__ import print_function

from contextional import GroupContextManager as GCM


class T(object):

    def assertThing(self, arg):
        print("here")


GCM.utilize_asserts(T)


with GCM("TEst") as t:

    @t.add_test("stuff")
    def test(case):
        case.assertThing(4)


t.create_tests(globals())
