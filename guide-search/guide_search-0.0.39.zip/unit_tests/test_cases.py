
import os
import json
import pytest
import requests
from urllib.parse import splitport

from guide_search import exceptions
from guide_search.esearch import Esearch, Dsl

# ----------------------------------- fixtures


@pytest.fixture
def root():
    return os.path.dirname(__file__)

@pytest.fixture
def index():
    return 'dev'

@pytest.fixture
def control():
    return 'knowledge_config/control'

@pytest.fixture
def eserver():
    return 'gl-know-ap33.lnx.lr.net:9200'

@pytest.fixture
def elasticsearch_version():
    return '1.4.5'


@pytest.fixture
def esearch(eserver, control, index):
    return Esearch(host='http://{}'.format(eserver),control=control)

@pytest.fixture
def dsl():
    return Dsl()

# ----------------------------------- tests


# def test_request_bad_url(esearch):
    # """
    # Bad url raises an exception
    # e.g. http://gl-know-ap33.lnx.lr.net:9201
    # """
    # url = esearch.make_url("")
    # url,port = splitport(url)
    # url = '{}:{}'.format(url,int(port)+1)
    # with pytest.raises(requests.exceptions.ConnectionError):
        # esearch.request(method='get', url=url)


def test_request_base_url(esearch, elasticsearch_version):
    """
    Base url returns correct elasticsearch version number
    e.g. http://gl-know-ap33.lnx.lr.net:9200
    """
    url = esearch.make_url("")
    r = esearch.request(method='get', url=url)
    assert r['status'] == 200
    assert r['version']['number'] == elasticsearch_version



def test_request_bad_route(esearch, index):
    """
    Right url + bad route raises a BadRequestError
    e.g.  http://gl-know-ap33.lnx.lr.net:9200/dev/spaghetti
    """
    with pytest.raises(exceptions.BadRequestError):
        url = esearch.make_url(index, "spaghetti")
        esearch.request(method='get', url=url, params=None, data=None, raw_response=False)


def test_makeurl(esearch, index, eserver):
    """
    make_url returns a well-formed URL
    """
    url = esearch.make_url(index, "articles", "bank")
    expected = 'http://{}/dev/articles/bank'.format(eserver)
    assert url == expected


@pytest.mark.parametrize("facet_filter", ["simple", "complex"])
def test_buildFacetFilter(esearch, root, facet_filter, dsl):

    filepath = os.path.join(root, 'fixtures', 'm_facet_filter', facet_filter + '.input')
    with open(filepath) as f:
        foci_selected = json.load(f)

    filepath = os.path.join(root, 'fixtures', 'm_facet_filter', facet_filter + '.result')
    with open(filepath) as f:
        expected = json.load(f)

    _filter = esearch.m_facet_filter(foci_selected)

    assert _filter == expected



def test_buildPage(esearch, dsl):
    """
    page correctly populates a dictionary of request fields based on:
        - the required page number (page)
        - number of results to be displayed per page (size)

    https://www.elastic.co/guide/en/elasticsearch/reference/5.1/search-request-from-size.html

    """
    
    assert esearch.page() == {'size': 5000}
    assert esearch.page(page=0) == {'size': 5000}
    assert esearch.page(page=1) == {'size': 5000}
    assert esearch.page(page=2) == {'size': 5000}
    assert esearch.page(size=10) == {'size': 10}
    assert esearch.page(size=10) == {'size': 10}
    assert esearch.page(size=10, page=0) == {'size': 10}
    assert esearch.page(size=10, page=1) == {'size': 10}
    assert esearch.page(size=10, page=2) == {'size': 10, 'from' : 10 }
    assert esearch.page(size=10, page=20) == {'size': 10, 'from' : 190 }
    assert esearch.page(size=10, page=-1) == {'size': 10}
    assert esearch.page(size=-10, page=1) == {'size': -10} # GE : TODO is this desired?

def test_buildSort(esearch):

    """
    buildSort correctly populates a dictionary of request fields based on:
        - sort = search_type = 'score', 'date', or 'popularity'
        - order = 'asc' or 'desc'

    https://www.elastic.co/guide/en/elasticsearch/reference/current/search-request-sort.html

    """

    assert dsl.buildSort() == {'sort': [{'_score': {'order': 'desc'}}]}
    assert dsl.buildSort(order='desc') == {'sort': [{'_score': {'order': 'desc'}}]}
    assert dsl.buildSort(sort='score') == {'sort': [{'_score': {'order': 'desc'}}]}
    assert dsl.buildSort(sort='score',order='desc') == {'sort': [{'_score': {'order': 'desc'}}]}
    assert dsl.buildSort(sort='date',order='asc') == {'sort': [{'master.lastmodified': {'order': 'asc'}}]}

def test_buildDsl(esearch, index):
    """
    buildDsl returns a well formed elasticsearch query

    """
    fields = ["id", "title", "scope", "master.document", "master.version", "sensitivity", "purpose"]
    expected = {
        'fields': ['id',
        'title',
        'scope',
        'master.document',
        'master.version',
        'sensitivity',
        'purpose'],
        'query': {
            'filtered': {'filter': {'bool': {'must': []}},
            'query': {'bool': {'should': []}}}
            },
        'size': 5000,
        'sort': 'id'}
    dsl = esearch.buildDsl(fields=fields, index=index)
    assert dsl == expected
    # this should now work: esearch.search(index,"articles",dsl)


@pytest.mark.parametrize('id', ['fr_gen_reg_lra2002'])
def test_search(esearch, index, id):
    """
    search successfully queries elasticsearch for a document by its ID.

    https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-ids-query.html#query-dsl-ids-query

    """
    dsl = {
        'query': {
            'ids': { 
            'values' : [id],
            }
        },
        'size': 2,
    }
    r = esearch.search(index=index, type="articles", dsl=dsl)
    assert len(r['hits']['hits']) == 1
    assert r['hits']['total'] == 1
    assert r['hits']['hits'][0]['_id'] == id


def test_get_documents(esearch,index):
    """
    get_documents returns a whole load of articles
    """
    r = esearch.get_documents(type="article", index=index)
    assert r['total'] > 1


# TODO
# def test_getAssociateList(esearch, index):
    # r = esearch.getAssociateList(index, "article")
    # pass


def test_get_articles(esearch, index):
    """
    get_articles returns a whole load of articles
    """
    r = esearch.get_articles(index=index)
    assert len(r) > 1


def test_get_items(esearch,index):
    r = esearch.get_items(index=index)
    assert len(r) > 1


def test_get_snippets(esearch,index):
    """
    """
    r = esearch.get_snippets(index=index)
    assert len(r) > 1


def test_get_document(esearch, index):
    """
    """
    r = esearch.get_document(index=index, type='article', id='fr_gen_reg_lra2002')
    assert 'First registration' in r['title']


def test_get_control(esearch):
    """
    """
    r = esearch.get_control(item='styles')
    assert 'legal_bold' in r.keys()

def test_get_similar(esearch, index):
    """
    """
    r = esearch.get_similar(index=index, keywords=['first','registration'])
    ids = [ i['id'][0] for i in r ]
    expected = ['admin_receiv_adrec', 'boundaries_electro', 'leases_regd_mortgage']
    assert not set(ids).difference(set(expected))

@pytest.mark.parametrize('id', ['work_all_tm_ji'])
def test_get_cluster(esearch, index,id):
    """
    """
    r = esearch.get_cluster(index=index, id=id, size=1)
    assert id in r[0]['id']

def test_get_cluster_ist(esearch, index):
    """
    """
    r = esearch.get_cluster_list(index=index)
    assert len(r) > 100

# def test_getWhere(esearch, index):
    # r = esearch.getWhere(index=index, item='styles')
    # import IPython; IPython.embed()

# def test_clearIndex ():
    # raise Exception('TODO')

# def test_postLog(esearch, index):
    # seq = '' update["seq"]
    # url = esearch.make_url(index, "commits", "{0}-{1}".format(index, seq)).strip()
    # r = esearch.request("get", url)
    # import IPython; IPython.embed()


# def test_getSuccess():
    # raise Exception('TODO')

# def test_getStatus():
    # raise Exception('TODO')

# def test_postEnd():
    # raise Exception('TODO')

# def test_resetUp():
    # raise Exception('TODO')

# def test_postUp():
    # raise Exception('TODO')

# def test_postKM():
    # raise Exception('TODO')

# def test_delKM():
    # raise Exception('TODO')