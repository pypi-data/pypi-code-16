from __future__ import print_function

import time
import unittest

from elasticsearch_dsl import Search

from cubicweb.devtools import testlib

from cubes.elasticsearch.search_helpers import compose_search

from cubes.elasticsearch.testutils import RealESTestMixin, BlogFTIAdapter


class ParentsSearchTC(RealESTestMixin, testlib.CubicWebTC):

    def test_parent_search(self):
        with self.admin_access.cnx() as cnx:
            with self.temporary_appobjects(BlogFTIAdapter):
                indexer = cnx.vreg['es'].select('indexer', cnx)
                indexer.create_index(custom_settings={
                    'mappings': {
                        'BlogEntry': {'_parent': {"type": "Blog"}},
                    }
                })
                test_structure = {
                    u'A': [u'Paris ceci', u'Nantes', u'Toulouse'],
                    u'B': [u'Paris cela'],
                    u'C': [u'Paris autre', u'Paris plage'],
                }
                for fa_title, facomp_contents in test_structure.items():
                    blog = cnx.create_entity('Blog',
                                             title=fa_title)
                    for facomp_content in facomp_contents:
                        cnx.create_entity('BlogEntry',
                                          entry_of=blog,
                                          title=facomp_content,
                                          content=facomp_content)
                cnx.commit()
            time.sleep(2)  # TODO find a way to have synchronous operations in unittests
            for query, number_of_results, first_result in (("Paris", 3, "C"),
                                                           ("Nantes", 1, "A")):
                search = compose_search(Search(index=self.config['index-name'],
                                               doc_type='Blog'),
                                        query,
                                        parents_for="BlogEntry",
                                        fields=['_all'],
                                        fuzzy=True)
                self.assertEquals(len(search.execute()), number_of_results)
                self.assertEquals(search.execute().to_dict()['hits']['hits'][0]['_source']['title'],
                                  first_result)


if __name__ == '__main__':
    unittest.main()
