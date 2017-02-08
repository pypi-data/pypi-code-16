# coding=utf-8
""" The sieves that check pronouns.

"""

from corefgraph.constants import SPAN, FORM, UTTERANCE, PREV_SPEAKER
from corefgraph.multisieve.features.constants import NUMBER, GENDER, PREDICATIVE_NOMINATIVE, MENTION, \
    PERSON, FIRST_PERSON, SECOND_PERSON, THIRD_PERSON, UNKNOWN, DEMONYM, PLEONASTIC
from corefgraph.multisieve.sieves.base import PronounSieve
from corefgraph.resources.dictionaries import pronouns

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class PronounMatch(PronounSieve):
    """ To mentions are coreferent if their surfaces are equals."""
    short_name = "PNM"
    # Filter options
    NO_PRONOUN_MENTION = False
    NO_STOP_WORDS = True
    INCOMPATIBLE_DISCOURSE = True
    NO_SUBJECT_OBJECT = False
    I_WITHIN_I = True
    SENTENCE_DISTANCE_LIMIT = 3

    def validate(self, mention, entity):
        """ Only pronouns can be used for this sieve

        :param mention: The mention to check.
        :param entity: The entity of the mention.
        """
        if not super(PronounMatch, self).validate(mention, entity):
            return False
        return True

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """A pronoun is coreferent with a candidate?

        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.

        :return: True or false
        """

        if not super(PronounMatch, self).are_coreferent(
                entity, mention, candidate_entity, candidate):
            return False

        representative_mention = self.entity_representative_mention(entity)

        if representative_mention[PREDICATIVE_NOMINATIVE] or \
                mention[PREDICATIVE_NOMINATIVE]:
            mention = representative_mention

        if not self.is_pronoun(mention):
            self.logger.debug("MENTION FILTERED: Not a pronoun.")
            return False
        if candidate.get(DEMONYM, False) and \
                not pronouns.no_organization(mention[FORM].lower()):
            self.logger.debug(
                "LINK FILTERED: Candidate is location and mention is not organization valid.")
            return False

        if not self.agree_attributes(entity=entity, candidate_entity=candidate_entity):
            self.logger.debug("LINK FILTERED: Attributes disagree.")
            return False

        if self.entity_person_disagree(mention_entity=entity, candidate_entity=candidate_entity):
            self.logger.debug("LINK FILTERED: Person Disagree.")
            self.invalid(entity_a=entity, mention_a=mention, entity_b=candidate_entity, mention_b=candidate)
            return False
        self.logger.debug("LINK ACCEPTED")
        self.meta[mention[FORM].lower()] += 1
        return True

    def entity_person_disagree(self, mention_entity, candidate_entity):
        """ Any mention of the entity or the candidate entity disagrees?
        :param mention_entity: The original cluster of mentions
        :param candidate_entity: The cluster of mentions that candidate is coreferent
        :return: True or False
        """
        for candidate in candidate_entity:
            for mention in mention_entity:
                if self.mention_person_disagree(mention, candidate, candidate_entity,
                                                mention_entity):
                    return True
        return False

    def mention_person_disagree(self, mention, candidate, candidate_entity, mention_entity):
        """ Check if the person of the mention and the candidate disagrees.

        :param mention: A mention, the main mention.
        :param candidate: A mention that may corefer to the main mention.
        :param candidate_entity: The entity that contains the candidate mention.
        :param mention_entity: The entity that contains the main mention.
        :return: True if the link breaks person agreement, otherwise True.
        """
        same_speaker = self.same_speaker(mention, candidate)
        mention_person = mention.get(PERSON)
        mention_number = mention.get(NUMBER)
        candidate_person = candidate.get(PERSON)
        candidate_number = candidate.get(NUMBER)
        # Same speaker
        # No same person and not is unknown or 3 person
        if same_speaker and (
                (mention_person != candidate_person) or (mention_number != candidate_number)):
            if mention_person == THIRD_PERSON and candidate_person == THIRD_PERSON:
                return False
            if mention_person != UNKNOWN and candidate_person != UNKNOWN:
                return True
        # Is not pronominal and the other mention first or second person
        if same_speaker:
            if not self.is_pronoun(mention):
                if candidate_person in (FIRST_PERSON, SECOND_PERSON):
                    return True
            if not self.is_pronoun(candidate):
                if mention_person in (FIRST_PERSON, SECOND_PERSON):
                    return True
        # Mention you and candidate previous to candidate
        if mention_person == SECOND_PERSON and candidate[SPAN] < mention[SPAN]:
            head_word = self.graph_builder.get_head_word(mention)
            utterance = head_word[UTTERANCE]
            if utterance == 0:
                return True
            prev_speaker = head_word[PREV_SPEAKER]
            if (prev_speaker is None) or MENTION not in prev_speaker:
                return True
            if prev_speaker in candidate_entity and candidate_person != FIRST_PERSON:
                return True

        if candidate_person == SECOND_PERSON and mention[SPAN] < candidate[SPAN]:
            head_word = self.graph_builder.get_head_word(candidate)
            utterance = head_word[UTTERANCE]
            if utterance == 0:
                return True
            prev_speaker = head_word[PREV_SPEAKER]
            if prev_speaker is None:
                return True
            if MENTION not in prev_speaker:
                return True
            if prev_speaker in mention_entity and mention_person != FIRST_PERSON:
                return True
        return False

    def log_mention(self, mention):
        """ The function that log the mention and all useful info for this sieve coreference
        resolution

        :param mention: The mention to show
        """
        self.logger.debug("MENTION -%s- %s", mention[FORM], mention[SPAN])

    def log_candidate(self, candidate):
        """ The function that show the candidate of a link and all the relevant info for the
        linking process.

        :param candidate:
        """
        self.logger.debug("CANDIDATE -%s- %s", candidate[FORM], candidate[SPAN])

    def context(self, mention_entity, mention, candidate_entity, candidate):
        """ Log out the entities and candidate context in a sieve relevant way.

        :param mention_entity: The Entity of the mention.
        :param mention: The mention of the wrong link.
        :param candidate_entity: The entity of the candidate .
        :param candidate: The candidate matched in the wrong link.
        """
        candidate_gender = self.entity_property(candidate_entity, GENDER)
        entity_gender = self.entity_property(mention_entity, GENDER)

        candidate_number = self.entity_property(candidate_entity, NUMBER)
        entity_number = self.entity_property(mention_entity, NUMBER)

        return " {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8}".format(
                         mention[FORM], mention.get(PERSON), entity_gender,
                         entity_number,
                         self.graph_builder.sentence_distance(mention, candidate),
                         candidate[FORM], candidate.get(PERSON), candidate_gender,
                         candidate_number, )


class SpanishPronounMatch(PronounMatch):
    short_name = "SPNM"
    UNRELIABLE = 1
    gold_check = True

    def validate(self, mention, entity):
        """ Only pronouns can be used for this sieve

        :param mention: The mention to check.
        :param entity: The entity of the mention.
        """
        if not super(SpanishPronounMatch, self).validate(mention, entity):
            return False
        if pronouns.relative(mention[FORM]):
            return False
        if mention[PLEONASTIC]:
            return False

        return True

    def are_coreferent(self, entity, mention, candidate_entity, candidate):
        """A pronoun is coreferent with a candidate?

        :param mention: The selected mention to represent the entity.
        :param entity: The entity that mention is part.
        :param candidate: The candidate that may corefer the entity.
        :param candidate_entity: The entity that candidate is part of it.

        :return: True or false

        """
        if pronouns.relative(candidate[FORM]):
            return False

        if candidate[PLEONASTIC]:
            return False

        return super(SpanishPronounMatch, self).are_coreferent(
                entity, mention, candidate_entity, candidate)
