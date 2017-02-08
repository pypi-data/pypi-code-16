# coding=utf-8

from corefgraph.resources.lambdas import list_checker, equality_checker, matcher, fail

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'

# Is a root constituent
root = list_checker(("root", "top", "ROOT", "TOP"))

# Is a clause
clauses = matcher("^S")

# Is a Noun phrase
noun_phrases = equality_checker("NP")

# Is a Verb phrase
verb_phrases = equality_checker("VP")

# Is a particle constituent
particle_constituents = equality_checker("PRT")

# Is an interjection constituent
past_participle_verb = equality_checker("VBN")

# Is an interjection constituent
interjections = equality_checker("INTJ")

# Is a NER annotated into semantic tree


# Is a simple or subordinated clause
simple_or_sub_phrase = list_checker(("S", "SBAR"))

adjectival_phrase = list_checker(("ADJP",))

adverbial_phrase = list_checker(("ADVP",))

#TODO Remove this check
mention_constituents = matcher("^NP")
enumerable = list_checker(("^NP", "^NML"))

head_rules = matcher("NP")