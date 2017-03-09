from contextional import GroupContextManager


with GroupContextManager("Predefined Group") as predefined_c:

    @predefined_c.add_test("value is still 2")
    def test(case):
        case.assertEqual(
            predefined_c.value,
            2,
        )


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

    with c.add_group("Child Group"):

        @c.add_setup
        def setUp():
            c.value += 1

        @c.add_test("value is now 3")
        def test():
            assert c.value == 3

        @c.add_teardown
        def tearDown():
            c.value -= 1

    c.includes(predefined_c)


c.create_tests(globals())
