# coding=utf-8
""" Ancora POS tag checkers.

Each elements in this module is a function that check if a POS tag.

Elements starting with _ is only for internal use.
"""
from corefgraph.resources.lambdas import fail, matcher

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

# features questions
male = matcher(r"^[ADPS]..M|^N.M|^V.....M")
female = matcher(r"^[ADP]..F|^N.F|^V.....F")
neutral = matcher(r"^[ADP]..N")

singular = matcher(r"^[ADPS]...S|^N..S|^V....S")
plural = matcher(r"^[ADPS]...P|^N..P|^V....P")

animate = fail()
inanimate = fail()
# Adecjtives
adjective = matcher(r"^A")

# Determinant
determinant = matcher("^D")
_possessive_determinant = matcher("^DP")

# Pronouns
# TODO Assure broad usage of these tags
_pronouns = matcher(r"^P")
pronouns = lambda x: _pronouns(x) or _possessive_determinant(x)
possessive_pronouns = matcher(r"^PX")
personal_pronouns = matcher(r"^PP")
relative_pronouns = matcher(r"^PR")
elliptic_pronoun = matcher(r"^PL")
interrogative_pronoun = matcher(r"^PT")

mention_pronouns = lambda x: personal_pronouns(x) or possessive_pronouns(x) or _possessive_determinant(x) \
    or relative_pronouns(x) or elliptic_pronoun(x)
#    or elliptic_pronoun(x)

# Nouns
all_nouns = matcher(r"^N")
common_nouns = matcher(r"^NC")
proper_nouns = matcher(r"^NP")
singular_common_nouns = lambda x: common_nouns(x) and singular(x)
plural_common_nouns = lambda x: common_nouns(x) and plural(x)

# Verbs
verbs = matcher(r"^V")
modals = fail()

# TODO No hay cardinales
mod_forms = lambda x: all_nouns(x) or adjective(x) or verbs(x) or cardinal(x)
indefinites = matcher(r"^.I")

# Enumerations
enumerable_mention_words = lambda x: all_nouns(x)
wh_words = fail()
subordinating_conjunction = fail()
conjunctions = matcher(r"^CC")

valid_inner_np = lambda x: conjunctions(x)

interjections = matcher("^I")

#cardinal = fail()
cardinal = matcher("^Z")
# TODO change to Semeval tagset
head_rules = matcher("^N")
