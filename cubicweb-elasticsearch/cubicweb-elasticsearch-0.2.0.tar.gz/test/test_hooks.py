import unittest
import time

from elasticsearch_dsl import Search

from cubicweb.devtools import testlib

from cubes.elasticsearch.testutils import RealESTestMixin, BlogFTIAdapter
from cubes.elasticsearch.search_helpers import compose_search


class ReindexOnRelationTests(RealESTestMixin, testlib.CubicWebTC):

    def test_es_hooks_modify_relation(self):
        with self.admin_access.cnx() as cnx:
            with self.temporary_appobjects(BlogFTIAdapter):
                indexer = cnx.vreg['es'].select('indexer', cnx)
                indexer.create_index(custom_settings={
                    'mappings': {
                        'BlogEntry': {'_parent': {"type": "Blog"}},
                    }
                })
                blog1 = cnx.create_entity('Blog', title=u'Blog')
                entity = cnx.create_entity('BlogEntry',
                                           title=u'Article about stuff',
                                           content=u'yippee',
                                           entry_of=blog1)
                blog2 = cnx.create_entity('Blog', title=u'Blog')
                cnx.commit()
                time.sleep(2)  # TODO find a way to have synchronous operations in unittests
                search = compose_search(Search(index=self.config['index-name'],
                                               doc_type='Blog'),
                                        'yippee',
                                        parents_for="BlogEntry",
                                        fields=['_all'])
                results = search.execute()
                self.assertEquals(len(results), 1)
                self.assertCountEqual([hit.eid for hit in results],
                                      [blog1.eid])
                blog2.cw_set(reverse_entry_of=entity)
                cnx.commit()
                time.sleep(2)  # TODO find a way to have synchronous operations in unittests
                search = compose_search(Search(index=self.config['index-name'],
                                               doc_type='Blog'),
                                        'yippee',
                                        parents_for="BlogEntry",
                                        fields=['_all'])
                results = search.execute()
                self.assertEquals(len(results), 2)
                self.assertCountEqual([hit.eid for hit in results],
                                      [blog1.eid, blog2.eid])


if __name__ == '__main__':
    unittest.main()
