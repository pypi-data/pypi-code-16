# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem_ref unit tests for schema"""

import unittest
from datetime import date
from contextlib import contextmanager

from six.moves import reduce

from cubicweb import ValidationError, Unauthorized, neg_role
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_saem_ref import (PERMISSIONS_GRAPHS, mandatory_rdefs,
                               optional_relations)

import testutils


def graph_relations(schema, parent_structure):
    """Given a parent structure of a composite graph (and a schema object),
    return relation information `(rtype, role)` sets where `role` is the role
    of the child in the relation for the following kinds of relations:

    * structural relations,
    * optional relations (cardinality of the child not in '1*'),
    * mandatory relations (cardinality of the child in '1*').
    """
    def concat_sets(sets):
        """Concatenate sets"""
        return reduce(lambda x, y: x | y, sets, set())

    optionals = concat_sets(
        optional_relations(schema, parent_structure).values())
    mandatories = set([
        (rdef.rtype, neg_role(role))
        for rdef, role in mandatory_rdefs(schema, parent_structure)])
    structurals = concat_sets(map(set, parent_structure.values()))
    return structurals, optionals, mandatories


@contextmanager
def assertValidationError(self, cnx):
    with self.assertRaises(ValidationError) as cm:
        yield cm
        cnx.commit()
    cnx.rollback()


@contextmanager
def assertUnauthorized(self, cnx):
    with self.assertRaises(Unauthorized) as cm:
        yield cm
        cnx.commit()
    cnx.rollback()


def assertUnauthorizedRQL(self, cnx, rql):
    with assertUnauthorized(self, cnx):
        cnx.execute(rql)


def create_published_agents_panel(cnx):
    for name, kind in (
        (u"Mr Pink", u"person"),
        (u"Adams", u"family"),
        (u"Direction de la communication", u"authority"),
    ):
        ar = testutils.authority_record(cnx, name, kind)
        cnx.commit()
        ar.cw_adapt_to('IWorkflowable').fire_transition('publish')
        cnx.commit()


class SchemaConstraintsTC(CubicWebTC):
    assertValidationError = assertValidationError

    def test_published_constraint_on_contact_point(self):
        """ create two agents: one published P and one not published N.
            create one OU and check that interface will only show P that can become its
            contact point
        """
        with self.admin_access.repo_cnx() as cnx:
            peter = testutils.agent(cnx, u'Peter')
            testutils.agent(cnx, u'Norton')
            cnx.commit()
            peter.cw_adapt_to('IWorkflowable').fire_transition('publish')
            ou = testutils.organization_unit(cnx, u'Alice')
            cnx.commit()
            rset = ou.unrelated('contact_point', 'Agent')
            self.assertEqual(rset.one().eid, peter.eid)

    def test_published_constraint_on_archival_agent(self):
        """ create two OU: one published P and one not published N.
            create one Organization and check that interface will only show P that can become its
            archival agent
        """
        with self.admin_access.repo_cnx() as cnx:
            pou = testutils.organization_unit(cnx, u'P OU', archival_roles=['archival'])
            testutils.organization_unit(cnx, u'N OU', archival_roles=['archival'])
            cnx.commit()
            pou.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            # should be created by testutils.organization_unit() above.
            authority = cnx.find('Organization', name=u'Default authority').one()
            rset = authority.unrelated('archival_unit', 'OrganizationUnit')
            self.assertEqual(rset.one().eid, pou.eid)

    def test_agent_authority_record_is_a_person(self):
        """Authority record for an agent is limited to person"""
        with self.admin_access.repo_cnx() as cnx:
            create_published_agents_panel(cnx)
            peter = testutils.agent(cnx, u'Peter')
            self.assertEqual(
                peter.unrelated('authority_record', 'AuthorityRecord').one(),
                cnx.find("AuthorityRecord", has_text=u"Mr Pink").one(),
            )

    def test_organization_unit_authority_record_is_a_authority(self):
        """Authority record for an organization unit is limited to authority"""
        with self.admin_access.repo_cnx() as cnx:
            create_published_agents_panel(cnx)
            pou = testutils.organization_unit(cnx, u'P OU')
            self.assertEqual(
                pou.unrelated('authority_record', 'AuthorityRecord').one(),
                cnx.find("AuthorityRecord", has_text=u"Direction de la communication").one(),
            )

    def test_organization_unit_contact_point_in_the_same_authority(self):
        """Create two agents on two distinct authorities. Create an organization unit and check that
        interface will only show consistent proposal for contact point
        """
        with self.admin_access.repo_cnx() as cnx:
            # Create an archival agent in a custom authority
            authority = testutils.authority_with_naa(cnx, name=u'boss club')
            jdoe = testutils.agent(cnx, u'jdoe', authority=authority)
            # Create another archival agent in the default authority
            norton = testutils.agent(cnx, u'Norton')
            cnx.commit()
            # Publish both agents (because of the published constraint)
            jdoe.cw_adapt_to('IWorkflowable').fire_transition('publish')
            norton.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            # Now create an organisation unit and check the unrelated list
            ou = testutils.organization_unit(cnx, u'Alice')
            cnx.commit()
            rset = ou.unrelated('contact_point', 'Agent')
            self.assertEqual(rset.one().eid, norton.eid)

    def test_organization_archival_unit_in_whatever_authority(self):
        """Create two organizations on two distinct authorities. Check that interface will show both
        of them as proposal for archival_agent of the default organization
        """
        with self.admin_access.repo_cnx() as cnx:
            # Create an organization unit in a custom authority
            authority = testutils.authority_with_naa(cnx, name=u'boss club')
            jdoe = testutils.organization_unit(cnx, u'jdoe', archival_roles=['archival'])
            # Create another archival organization unit in the default authority
            norton = testutils.organization_unit(cnx, u'Norton', archival_roles=[u'archival'])
            cnx.commit()
            # Publish both organization units (because of the published constraint)
            jdoe.cw_adapt_to('IWorkflowable').fire_transition('publish')
            norton.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            # Now check the unrelated list for authority's archival_unit
            authority = cnx.find('Organization', name=u'Default authority').one()
            rset = authority.unrelated('archival_unit', 'OrganizationUnit')
            self.assertEqual(len(rset), 2)

    def test_agent_authority_consistency(self):
        with self.admin_access.repo_cnx() as cnx:
            authority1 = testutils.authority_with_naa(cnx)
            authority2 = testutils.authority_with_naa(cnx, name=u'boss club')
            user = self.create_user(cnx, login=u'user', groups=('users',))
            cnx.commit()
            # jdoe is in authority2 and user has no authority: OK
            jdoe = testutils.agent(cnx, u'jdoe', authority=authority2)
            jdoe.cw_set(agent_user=user)
            cnx.commit()
            # jdoe is in authority2 and attempt to set user in authority1: KO
            with self.assertValidationError(cnx):
                user.cw_set(authority=authority1)
                cnx.commit()
            cnx.rollback()
            # break link between agent and user
            jdoe.cw_set(agent_user=None)
            cnx.commit()
            user.cw_set(authority=authority1)
            # jdoe is in authority2, user in authority1 and attempt to link them KO
            with self.assertValidationError(cnx):
                jdoe.cw_set(agent_user=user)


class AuthorityRecordTC(CubicWebTC):
    assertUnauthorizedRQL = assertUnauthorizedRQL

    def test_fti(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('AgentKind', name=u'Queen')
            agent = testutils.authority_record(cnx, u'Guenievre', kind=u'Queen',
                                               end_date=date(476, 2, 9))
            address = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                        postalcode=u'31400', city=u'Toulouse')
            cnx.create_entity('AgentPlace', name=u'place', place_address=address, place_agent=agent)
            cnx.create_entity('AgentFunction', name=u'function', function_agent=agent)
            cnx.create_entity('LegalStatus', term=u'legal status', legal_status_agent=agent)
            cnx.commit()
            for search in (u'guenievre', u'europe', u'place', u'function', u'legal status'):
                with self.subTest(search=search):
                    self.assertEqual(cnx.execute('AuthorityRecord X WHERE X has_text %(search)s',
                                                 {'search': search}).one().eid, agent.eid)

    def test_graph_structure(self):
        graph = PERMISSIONS_GRAPHS['AuthorityRecord'](self.schema)
        expected = {
            'AgentFunction': {('function_agent', 'subject'): set(['AuthorityRecord'])},
            'AgentPlace': {('place_agent', 'subject'): set(['AuthorityRecord'])},
            'Citation': {('has_citation', 'object'): set([
                'GeneralContext', 'Mandate', 'Occupation', 'AgentFunction',
                'AgentPlace', 'History', 'LegalStatus',
            ])},
            'EACOtherRecordId': {('eac_other_record_id_of', 'subject'):
                                 set(['AuthorityRecord'])},
            'EACResourceRelation': {('resource_relation_agent', 'subject'):
                                    set(['AuthorityRecord'])},
            'EACSource': {('source_agent', 'subject'): set(['AuthorityRecord'])},
            'GeneralContext': {('general_context_of', 'subject'): set(['AuthorityRecord'])},
            'History': {('history_agent', 'subject'): set(['AuthorityRecord'])},
            'LegalStatus': {('legal_status_agent', 'subject'): set(['AuthorityRecord'])},
            'Mandate': {('mandate_agent', 'subject'): set(['AuthorityRecord'])},
            'NameEntry': {('name_entry_for', 'subject'): set(['AuthorityRecord'])},
            'Occupation': {('occupation_agent', 'subject'): set(['AuthorityRecord'])},
            'PostalAddress': {('place_address', 'object'): set(['AgentPlace'])},
            'Structure': {('structure_agent', 'subject'): set(['AuthorityRecord'])},
        }
        struct = dict(
            (k, dict((rel, set(targets)) for rel, targets in v.items()))
            for k, v in graph.parent_structure('AuthorityRecord').items())
        self.assertEqual(struct, expected)

    def test_optional_relations(self):
        graph = PERMISSIONS_GRAPHS['AuthorityRecord'](self.schema)
        structure = graph.parent_structure('AuthorityRecord')
        opts = optional_relations(self.schema, structure)
        expected = {}
        self.assertEqual(opts, expected)

    def test_relations_consistency(self):
        graph = PERMISSIONS_GRAPHS['AuthorityRecord'](self.schema)
        structure = graph.parent_structure('AuthorityRecord')
        structurals, optionals, mandatories = graph_relations(
            self.schema, structure)
        self.assertEqual(structurals - optionals, mandatories)


class ConceptSchemeTC(CubicWebTC):

    def test_graph_structure(self):
        graph = PERMISSIONS_GRAPHS['ConceptScheme'](self.schema)
        expected = {
            'Concept': {('in_scheme', 'subject'): ['ConceptScheme']},
            'Label': {('label_of', 'subject'): ['Concept']},
        }
        self.assertEqual(graph.parent_structure('ConceptScheme'),
                         expected)

    def test_optional_relations(self):
        graph = PERMISSIONS_GRAPHS['ConceptScheme'](self.schema)
        opts = optional_relations(self.schema,
                                  graph.parent_structure('ConceptScheme'))
        expected = {}
        self.assertEqual(opts, expected)

    def test_relations_consistency(self):
        graph = PERMISSIONS_GRAPHS['ConceptScheme'](self.schema)
        structure = graph.parent_structure('ConceptScheme')
        structurals, optionals, mandatories = graph_relations(
            self.schema, structure)
        self.assertEqual(structurals - optionals, mandatories)


class SecurityTC(CubicWebTC):
    """Test case for permissions set in the schema"""
    assertUnauthorized = assertUnauthorized

    def test_agentkind_type(self):
        with self.admin_access.cnx() as cnx:
            kind = cnx.find('AgentKind', name=u'person').one()
            # no one can update nor delete a kind
            with self.assertRaises(Unauthorized):
                kind.cw_set(name=u'gloups')
                cnx.commit()
            cnx.rollback()
            with self.assertRaises(Unauthorized):
                kind.cw_delete()
                cnx.commit()
            cnx.rollback()

    def test_agent_kind_relation(self):
        """Test we can only change kind from unknown to another."""
        with self.admin_access.repo_cnx() as cnx:
            agent = testutils.authority_record(cnx, u'bob', kind=u'unknown-agent-kind')
            cnx.commit()
            agent.cw_set(agent_kind=cnx.find('AgentKind', name=u'person').one())
            cnx.commit()
            with self.assertRaises(Unauthorized):
                agent.cw_set(agent_kind=cnx.find('AgentKind', name=u'authority').one())

    def test_authority_type(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'user', groups=('users',))
            cnx.commit()
        with self.new_access('user').client_cnx() as cnx:
            with self.assertUnauthorized(cnx):
                testutils.authority_with_naa(cnx, name=u'dream team')

    def test_authority_relation(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'user', groups=('users',),
                             authority=testutils.authority_with_naa(cnx))
            agent = testutils.agent(cnx, u'user')
            authority = testutils.authority_with_naa(cnx, name=u'dream team')
            cnx.commit()
            # even manager can't change an agent's authority
            with self.assertUnauthorized(cnx):
                agent.cw_set(authority=authority.eid)
        with self.new_access('user').client_cnx() as cnx:
            agent = cnx.entity_from_eid(agent.eid)
            # user can't change its own authority
            with self.assertUnauthorized(cnx):
                agent.cw_set(authority=authority.eid)
            # user can't create an agent in another authority than its own
            with self.assertUnauthorized(cnx):
                testutils.agent(cnx, u'new agent', authority=authority.eid)
            # though he can add an agent to its own authority
            testutils.agent(cnx, u'new agent')
            cnx.commit()

    def test_agent_user(self):
        with self.admin_access.repo_cnx() as cnx:
            user1 = self.create_user(cnx, login=u'user1', groups=('users',),
                                     authority=testutils.authority_with_naa(cnx))
            user2 = self.create_user(cnx, login=u'user2', groups=('users',),
                                     authority=testutils.authority_with_naa(cnx))
            agent = testutils.agent(cnx, u'user1', agent_user=user1)
            cnx.commit()
        with self.new_access('user1').client_cnx() as cnx:
            agent = cnx.entity_from_eid(agent.eid)
            # user can't change its own user
            with self.assertUnauthorized(cnx):
                agent.cw_set(agent_user=user2.eid)
            with self.assertUnauthorized(cnx):
                agent.cw_set(agent_user=None)
            # user can't create an agent and specify its associated user
            with self.assertUnauthorized(cnx):
                testutils.agent(cnx, u'user2', agent_user=user2.eid)
            agent2 = testutils.agent(cnx, u'user2')
            cnx.commit()
            with self.assertUnauthorized(cnx):
                agent2.cw_set(agent_user=user2.eid)

    def test_authority_record_base(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'toto', groups=('users', 'guests'),
                             authority=testutils.authority_with_naa(cnx))
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            function = cnx.create_entity('AgentFunction', name=u'grouillot')
            testutils.authority_record(cnx, u'bob', reverse_function_agent=function)
            cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute('DELETE U in_group G WHERE U login "toto", G name "users"')
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            agent = cnx.find('AuthorityRecord', has_text=u'bob').one()
            # guest user can't modify an authority record
            with self.assertUnauthorized(cnx):
                agent.cw_set(record_id=u'bobby')
            with self.assertUnauthorized(cnx):
                agent.reverse_function_agent[0].cw_set(name=u'director')

    def test_authority_record_wf_permissions(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'toto', groups=('users', 'guests'),
                             authority=testutils.authority_with_naa(cnx))
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            function = cnx.create_entity('AgentFunction', name=u'grouillot')
            agent = testutils.authority_record(cnx, u'bob', reverse_function_agent=function)
            cnx.commit()
            iwf = agent.cw_adapt_to('IWorkflowable')
            iwf.fire_transition('publish')
            cnx.commit()
            # we can still modify a published agent
            agent.reverse_name_entry_for[0].cw_set(parts=u'bobby')
            function.cw_set(name=u'director')
            cnx.commit()

    def test_update_root_badgroup(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'toto', groups=('users', 'guests'))
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            testutils.setup_profile(cnx, title=u'pp')
            cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute(
                'DELETE U in_group G WHERE U login "toto", G name "users"')
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            profile = cnx.find('SEDAArchiveTransfer', title=u'pp').one()
            with self.assertUnauthorized(cnx):
                profile.cw_set(title=u'qq')

    def test_update_child(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'toto', groups=('users', 'guests'),
                             authority=testutils.authority_with_naa(cnx))
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            record = testutils.authority_record(cnx, u'bob')
            function = cnx.create_entity('AgentFunction', name=u'boss',
                                         function_agent=record)
            cnx.commit()
            # Draft -> OK.
            function.cw_set(name=u'grouyo')
            cnx.commit()
            cnx.create_entity('GeneralContext', content=u'plop',
                              general_context_of=record)
            cnx.commit()
            iwf = record.cw_adapt_to('IWorkflowable')
            iwf.fire_transition('publish')
            cnx.commit()
            # Published -> still OK for record.
            record.cw_set(record_id=u'big boss')
            cnx.commit()
            cnx.create_entity('History', text=u'yellow sponge',
                              history_agent=record)
            cnx.commit()

    def test_sedaprofile_wf_permissions(self):
        with self.admin_access.repo_cnx() as cnx:
            profile = testutils.setup_profile(cnx, title=u'pp')
            cnx.commit()
            # Profile in draft, modifications are allowed.
            profile.cw_set(title=u'ugh')
            cnx.commit()
            # Profile published, no modification allowed.
            profile.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()

    def test_conceptscheme_wf_permissions(self):
        with self.admin_access.cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', ark_naa=testutils.naa(cnx))
            cnx.commit()
            # in draft, modifications are allowed.
            concept = scheme.add_concept(u'blah')
            cnx.commit()
            # published, can't modify existing content.
            scheme.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            with self.assertUnauthorized(cnx):
                scheme.cw_set(description=u'plop')
            with self.assertUnauthorized(cnx):
                concept.preferred_label[0].cw_set(label=u'plop')
            # though addition of new concepts / labels is fine
            new_concept = scheme.add_concept(u'plop')
            cnx.commit()
            new_label = cnx.create_entity('Label', label=u'arhg', label_of=concept)
            cnx.commit()
            # while deletion is fine for label but not for concept nor scheme
            new_label.cw_delete()
            cnx.commit()
            with self.assertUnauthorized(cnx):
                scheme.cw_delete()
            with self.assertUnauthorized(cnx):
                new_concept.cw_delete()


if __name__ == '__main__':
    unittest.main()
