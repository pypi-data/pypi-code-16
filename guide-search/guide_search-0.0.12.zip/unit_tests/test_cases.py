
import os
import json
import guide_search.esearch as e
import pytest


root = os.path.dirname(__file__)
eserver = 'gl-know-ap33.lnx.lr.net:9200'
index = 'dev'
control = 'knowledge_config/control'

esearch = e.Esearch('http://{}'.format(eserver),
                    index, control)


def test_makeurl():
    url = esearch.makeUrl("dev", "articles", "bank")
    expected = 'http://{}/dev/articles/bank'.format(eserver)
    assert url == expected


@pytest.mark.parametrize("facet_filter", ["simple", "complex"])
def test_buildFacetFilter(facet_filter):
    folder = os.path.join(root, 'fixtures', 'buildFacetFilter')
    filepath = os.path.join(folder, facet_filter + '.input')
    with open(filepath) as f:
        foci_selected = json.load(f)
    folder = os.path.join(root, 'fixtures', 'buildFacetFilter')
    filepath = os.path.join(folder, facet_filter + '.result')
    with open(filepath) as f:
        expected = json.load(f)


    filter = esearch.buildFacetFilter(foci_selected)

    assert filter == expected
