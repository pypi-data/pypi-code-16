# Copyright 2017 Graham Binns. This software is licensed under the MIT
# license. See the LICENSE file for more information.
"""Tests for usefulenums.enum."""


from unittest import TestCase

from usefulenums.enum import Enum


class EnumInitTestCase(TestCase):
    """Tests for Enum.__init__()."""

    def test_accepts_three_tuples_as_arguments(self):
        # __init__() will take three-tuples as arguments for setting up
        # enumeration items.
        try:
            Enum((1, "MY_FIRST_VALUE", "Display text"))
        except ValueError:
            self.fail("Enum() raised a ValueError when accepting a 3-tuple.")

    def test_accepts_two_tuples_as_arguments(self):
        # __init__() will take two-tuples as arguments for setting up
        # enumeration items.
        try:
            Enum(("MY_FIRST_VALUE", "Display text"))
        except ValueError:
            self.fail("Enum() raised a ValueError when accepting a 2-tuple.")

    def test_rejects_mixed_two_and_three_tuples(self):
        # __init__() does not allow 2-tuples to be mixed with 3-tuples.
        # Whichever comes first wins.
        self.assertRaises(
            ValueError, Enum, (1, "MY_FIRST_VALUE", "Display text"),
            ("MY_SECOND_VALUE", "Display text 2"))

    def test_assigns_2_tuple_ids_automatically(self):
        # When 2-tuples are passed to __init__(), IDs are assigned to
        # the items in order.
        enum = Enum(
            ("MY_FIRST_VALUE", "Display text"),
            ("MY_SECOND_VALUE", "Display text 2"))

        self.assertEqual(0, enum._id_mappings["MY_FIRST_VALUE"])
        self.assertEqual(1, enum._id_mappings["MY_SECOND_VALUE"])

    def test_python_name_must_conform_to_regex(self):
        # The python_name passed to __init__() must contain uppercase
        # letters, underscores or numbers only, with no leading digits.
        invalid_names = [
            "Not conforming at all",
            "1_NO_LEADING_NUMBERS",
            "UPPERCASE_letters_ONLY",
        ]

        for invalid_name in invalid_names:
            self.assertRaises(
                ValueError, Enum, (invalid_name, ""))
            self.assertRaises(
                ValueError, Enum, (1, invalid_name, ""))


class EnumGetAttrTestCase(TestCase):
    """Tests for Enum.__getattr__()."""

    def test_returns_id_for_python_name(self):
        # When Enum.FOO is accessed, the ID associated with the
        # python_name `FOO` is returned.
        enum = Enum((1, "TEST_VALUE", "Test value"))
        self.assertEqual(1, enum.TEST_VALUE)

    def test_raises_attribute_error_if_no_such_name(self):
        # If a given enum item does not exist, trying to access it will
        # raise an AttributeError.
        enum = Enum((1, "TEST_VALUE", "Test value"))
        self.assertRaises(AttributeError, lambda: enum.DOES_NOT_EXIST)


class EnumAsChoicesTestCase(TestCase):
    """Tests for Enum.as_choices()."""

    def test_returns_ordered_key_value_pairs(self):
        # Enum.as_choices() returns the enum's items in ID order as (ID,
        # display_name) pairs.
        enum = Enum(
            (1, "CHOICE_1", "Choice one"),
            (2, "CHOICE_2", "Choice two"),
            (0, "CHOICE_0", "Choice zero"),
        )
        expected_choices = (
            (0, "Choice zero"),
            (1, "Choice one"),
            (2, "Choice two"),
        )
        self.assertEqual(expected_choices, enum.as_choices())
