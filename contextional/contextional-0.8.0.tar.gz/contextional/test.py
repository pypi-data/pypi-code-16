from __future__ import print_function

from contextional import GroupContextManager as GCM


class T(object):

    def assertThing(self, arg):
        assert arg == 4


GCM.utilize_asserts(T)



#
# with GCM("TEst") as t:
#
#     @t.add_test("stuff")
#     def test(case):
#         case.assertThing(4)
#
#     with t.add_group("other"):
#         @t.add_test("stuff")
#         def test(case):
#             case.assertThing(2)
#
#
# with GCM("Predefined Group") as PG:
#
#     @PG.add_test("value is 1")
#     def test(case):
#         case.assertEqual(
#             PG.value,
#             1,
#         )
#
#     with PG.add_group("Sub Group"):
#
#         @PG.add_test("value is still 1")
#         def test(case):
#             case.assertEqual(
#                 PG.value,
#                 1,
#             )

def multiplier(num_1, num_2):
    return num_1 * num_2


with GCM("value test") as vt:

    @vt.add_test("value")
    def test(case):
        case.assertEqual(
            vt.value,
            vt.expected_value,
        )

with GCM("Main Group") as MG:

    with MG.add_group("2 and 3"):

        @MG.add_setup
        def setUp():
            MG.value = multiplier(2, 3)
            MG.expected_value = 6

        MG.merge(vt)

    with MG.add_group("3 and 5"):

        @MG.add_setup
        def setUp():
            MG.value = multiplier(3, 5)
            MG.expected_value = 15

        MG.merge(vt)


MG.create_tests(globals())
