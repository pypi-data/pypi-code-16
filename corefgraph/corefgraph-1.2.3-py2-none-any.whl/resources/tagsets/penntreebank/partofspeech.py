# coding=utf-8
""" Penntreebank POS tag checkers.

Each elements in this module is a function that check if a POS tag.

Elements starting with _ is only for internal use.
"""
from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

# Inner usage only
_personal_pronoun = "PRP"
_possessive_pronoun = "PRP$"
_wh_pronoun = "WP"
_wh_possessive_pronoun = "WP$"
_wh_determiner = "WDT"
_wh_adverb = "WRB"
_verbs_list = ("VB", "VBD", "VBG", "VBN", "VBP ", "VBZ")
_modal = "MD"
_noun = "NN"
_noun_plural = "NNS"
_interjection = "UH"
_proper_noun = "NNP"
_proper_noun_plural = "NNPS"

_adjective = "JJ"
_adjective_comparative = "JJR"
_adjective_superlative = "JJS"

_conjunctions = ("CC",)

# comma = equality_checker(",")

# Usable functions

# features questions
female = fail()
male = fail()
neutral = fail()

singular = matcher("^NNP?$")
plural = matcher("^NNP?S$")

animate = fail()
inanimate = fail()

# Adecjtives
adjectives = list_checker((_adjective, _adjective_comparative, _adjective_superlative))
adjective = list_checker((_adjective,))
# pronouns
personal_pronouns = list_checker((_personal_pronoun, _possessive_pronoun))
relative_pronouns = list_checker((_wh_pronoun, _wh_possessive_pronoun))
pronouns = list_checker((_personal_pronoun, _possessive_pronoun, _wh_pronoun, _wh_possessive_pronoun))
# mention_pronouns = lambda x: relative_pronouns(x) or personal_pronouns(x)
mention_pronouns = matcher("^PRP")

# Nouns
singular_common_nouns = equality_checker(_noun)
plural_common_nouns = equality_checker(_noun_plural)
proper_nouns = list_checker((_proper_noun, _proper_noun_plural))
all_nouns = lambda x: x is not None and (singular_common_nouns(x) or plural_common_nouns(x) or proper_nouns(x))

# Verbs
verbs = list_checker(_verbs_list)
modals = equality_checker(_modal)
# mod_forms = lambda x: all_nouns(x) or adjectives(x) or verbs(x) or cardinal(x)
mod_forms = lambda x: x is not None and (x.startswith("N") or x.startswith("JJ") or x.startswith("V") or x == "CD")
indefinite = fail

# Enumerations
# enumerable_mention_words = list_checker((_proper_noun, "NML"))
# TODO remove NP and put in constituent
enumerable_mention_words = matcher("^NNP")

conjunctions = list_checker(_conjunctions)
wh_words = list_checker((_wh_pronoun, _wh_possessive_pronoun, _wh_determiner, _wh_adverb))
subordinating_conjunction = equality_checker("IN")
valid_inner_np = lambda x: conjunctions(x)

extended_inner_np = lambda x: conjunctions(x) or wh_words(x) or subordinating_conjunction(x)
extended_inner_np_b = lambda x: conjunctions(x) or wh_words(x)
extended_inner_np_c = lambda x: conjunctions(x) or subordinating_conjunction(x)

interjections = equality_checker(_interjection)
cardinal = matcher("^CD")

head_rules = matcher("^N")

verbs_past_particicle = matcher("VBN")