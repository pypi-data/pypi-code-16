import unittest
from gr import Gr
from reader import Entry, PLUS, MINUS




class TestGr(unittest.TestCase):

    def test_gr_add(self):
        one   = Entry(0, 10, 20, "", PLUS)
        two   = Entry(0, 21, 30, "", PLUS)
        three = Entry(1, 15, 25, "", PLUS)

        range1 = Gr().add(three)
        range1.add(two)
        range1.add(one)

        range1.sort()

        self.assertEqual(range1.number_of_components, 3)
        self.assertEqual([entry for entry in range1.all_entries], [one, two, three])


    def test_gr_reader(self):
        one   = Entry(0, 10, 20, "", PLUS)
        two   = Entry(0, 21, 30, "", PLUS)
        three = Entry(1, 15, 25, "", PLUS)

        range1 = Gr([three, two, one])

        self.assertEqual(range1.number_of_components, 3)
        self.assertEqual([entry for entry in range1.all_entries], [one, two, three])


    def test_gr_merge(self):
        one   = Entry(0, 10, 20, "", PLUS)
        two   = Entry(0, 21, 30, "", PLUS)
        three = Entry(0, 31, 40, "", PLUS)
        four  = Entry(0, 9, 41, "", PLUS)
        five  = Entry(0, 99, 100, "", PLUS)
   
        merged = Gr([three, two]).merged

        self.assertEqual(merged.number_of_components, 1)
        self.assertEqual([entry for entry in merged.all_entries], [Entry(0, 21, 40, "", PLUS)])

        merged = Gr([three, two, one]).merged

        self.assertEqual(merged.number_of_components, 1)
        self.assertEqual([entry for entry in merged.all_entries], [Entry(0, 10, 40, "", PLUS)])

        merged = Gr([four, three, two, one]).merged

        self.assertEqual(merged.number_of_components, 1)
        self.assertEqual([entry for entry in merged.all_entries], [Entry(0, 9, 41, "", PLUS)])

        merged = Gr([five, four, three, two, one]).merged

        self.assertEqual(merged.number_of_components, 2)
        self.assertEqual([entry for entry in merged.all_entries], [Entry(0, 9, 41, "", PLUS), five])







































if __name__ == '__main__':
    unittest.main()






