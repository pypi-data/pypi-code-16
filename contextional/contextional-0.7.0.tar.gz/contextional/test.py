from contextional import GroupContextManager


class Stuff(object):
    def assertThing(self, value):
        if value:
            pass
        else:
            raise AssertionError("No Good!")


GroupContextManager.utilize_asserts(Stuff)


with GroupContextManager("Predefined Group") as predefined_c:

    @predefined_c.add_test("value is still 2")
    def test(case):
        case.assertEqual(
            predefined_c.value,
            2,
        )

    with predefined_c.add_group("some sub group"):

        @predefined_c.add_test("new sub test")
        def test(case):
            pass


with GroupContextManager("Main Group") as c:

    @c.add_setup
    def setUp():
        c.value = 0

    @c.add_test_setup
    def testSetUp():
        c.value += 1

    @c.add_test("value is 1")
    def test(case):
        case.assertEqual(
            c.value,
            1,
        )

    @c.add_test("value is 2")
    def test():
        assert c.value == 2

    params = (
        {
            "num_1": 1,
            "num_2": 2,
            "num_3": 3,
        },
        {
            "num_3": 3,
            "num_2": 2,
            "num_1": 1,
        },
    )
    with c.add_group("Child Group", params=params):

        @c.add_setup
        def setUp(num_1, num_2, num_3):
            c.sum = num_1 + num_2 + num_3

        @c.add_test("sum is 6")
        def test(case):
            case.assertEqual(c.sum, 6)

    params = {
        "set #1": (1, 2, 3),
        "set #2": (3, 2, 1),
    }
    with c.add_group("Another Child Group", params=params):

        @c.add_setup
        def setUp(num_1, num_2, num_3):
            c.sum = num_1 + num_2 + num_3

        @c.add_test("sum is 6")
        def test(case):
            case.assertEqual(c.sum, 6)

    with c.add_group("Child Group"):

        @c.add_setup
        def setUp():
            c.value += 1

        @c.add_test("value is now 3")
        def test():
            assert c.value == 3

        @c.add_test("new assert")
        def test(case):
            case.assertThing(True)

        @c.add_test("new false assert")
        def test(case):
            case.assertThing(False)

        @c.add_teardown
        def tearDown():
            c.value -= 1

    c.includes(predefined_c)


c.create_tests(globals())
