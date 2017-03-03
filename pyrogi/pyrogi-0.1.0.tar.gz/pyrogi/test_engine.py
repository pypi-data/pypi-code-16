import unittest
from engine import parse_text_into_characters

class TestParseTextIntoCharacters(unittest.TestCase):
    def test_plain_characters(self):
        self.assertEqual(parse_text_into_characters(''), [])
        self.assertEqual(parse_text_into_characters('a'), ['a'])
        self.assertEqual(parse_text_into_characters('ab'), ['a', 'b'])
        self.assertEqual(parse_text_into_characters('abcdefghijk'), ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k'])
        self.assertEqual(parse_text_into_characters('a b'), ['a', ' ', 'b'])
        self.assertEqual(parse_text_into_characters('a b '), ['a', ' ', 'b', ' '])
        self.assertEqual(parse_text_into_characters('a  b'), ['a', ' ', ' ', 'b'])

    def test_escape_characters(self):
        self.assertEqual(parse_text_into_characters('\\\\'), ['\\'])
        self.assertEqual(parse_text_into_characters('\\['), ['['])
        self.assertEqual(parse_text_into_characters('\\]'), [']'])
        self.assertEqual(parse_text_into_characters('oauhstt tot\\] ath'), ['o', 'a', 'u', 'h', 's', 't', 't', ' ', 't', 'o', 't', ']', ' ', 'a', 't', 'h'])
        self.assertEqual(parse_text_into_characters('oauhstt to[t\\]] ath'), ['o', 'a', 'u', 'h', 's', 't', 't', ' ', 't', 'o', 't]', ' ', 'a', 't', 'h'])
        self.assertEqual(parse_text_into_characters('oauhst[t t]o[t\\\\] ath'), ['o', 'a', 'u', 'h', 's', 't', 't t', 'o', 't\\', ' ', 'a', 't', 'h'])

        self.assertRaisesRegex(ValueError, "Invalid escape character 'a'.", parse_text_into_characters, '\\a')
        self.assertRaisesRegex(ValueError, "Invalid escape character '8'.", parse_text_into_characters, '\\8')
        self.assertRaisesRegex(ValueError, "Invalid escape character '8'.", parse_text_into_characters, 'sntahoe a[ot]uhoa\\8 othuas')
        self.assertRaisesRegex(ValueError, "Invalid escape character '8'.", parse_text_into_characters, 'sntahoe a[ot]uhoa[\\8] othuas')

        self.assertRaisesRegex(ValueError, "The '\\\\' at the end of the string isn't escaping anything.", parse_text_into_characters, '\\')
        self.assertRaisesRegex(ValueError, "The '\\\\' at the end of the string isn't escaping anything.", parse_text_into_characters, 'to[u]hats[ ][ot]out tat thot\\')

    def test_groups(self):
        self.assertEqual(parse_text_into_characters('[a]'), ['a'])
        self.assertEqual(parse_text_into_characters('[abcdefghijk]'), ['abcdefghijk'])
        self.assertEqual(parse_text_into_characters('abc [def][hi]toh[oo]'), ['a', 'b', 'c', ' ', 'def', 'hi', 't', 'o', 'h', 'oo'])

        self.assertRaisesRegex(ValueError, 'You cannot end a character group that you have not started.', parse_text_into_characters, ']')
        self.assertRaisesRegex(ValueError, 'You cannot end a character group that you have not started.', parse_text_into_characters, 'tohut otuha]')
        self.assertRaisesRegex(ValueError, 'You cannot end a character group that you have not started.', parse_text_into_characters, 'tou[ot][,,]ot<t   to[iho][otu]]')

        self.assertRaisesRegex(ValueError, 'You started a character group but did not finish it.', parse_text_into_characters, '[')
        self.assertRaisesRegex(ValueError, 'You started a character group but did not finish it.', parse_text_into_characters, '[otuh')
        self.assertRaisesRegex(ValueError, 'You started a character group but did not finish it.', parse_text_into_characters, '[ otat')
        self.assertRaisesRegex(ValueError, 'You started a character group but did not finish it.', parse_text_into_characters, '[o].4c,9sz[332] o,y092[')

        self.assertRaisesRegex(ValueError, 'You cannot start a character group within another group.', parse_text_into_characters, '[[a]]')
        self.assertRaisesRegex(ValueError, 'You cannot start a character group within another group.', parse_text_into_characters, '[35,.p[a] o]')
        self.assertRaisesRegex(ValueError, 'You cannot start a character group within another group.', parse_text_into_characters, '[,tou]ou, ,[oot. o[ot. teo ]otu]')

        self.assertRaisesRegex(ValueError, 'You cannot have an empty character group.', parse_text_into_characters, '[]')
        self.assertRaisesRegex(ValueError, 'You cannot have an empty character group.', parse_text_into_characters, 'aeu[]')
        self.assertRaisesRegex(ValueError, 'You cannot have an empty character group.', parse_text_into_characters, '[]ouu')
        self.assertRaisesRegex(ValueError, 'You cannot have an empty character group.', parse_text_into_characters, 'aeaueu[]au')
        self.assertRaisesRegex(ValueError, 'You cannot have an empty character group.', parse_text_into_characters, '[ateu,] otu,[ot,] ,0o[ote][oth,][][tout,t][out,][out,]')
