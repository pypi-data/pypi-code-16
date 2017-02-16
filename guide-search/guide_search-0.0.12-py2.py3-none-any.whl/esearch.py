import requests
import json
import datetime

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
from posixpath import join as posixjoin
from .exceptions import (
    JSONDecodeError,
    BadRequestError,
    ResourceNotFoundError,
    ConflictError,
    PreconditionError,
    ServerError,
    ServiceUnreachableError,
    UnknownError,
    ResultParseError,
    CommitError,
    ValidationError,
    )

"""
guide-search

interface to the guidance index in elasticsearch

currently built for elasticseach v1.4

# ES5 : True was unquoted changed this to "true"  - ES1 break ?


"""


class Dsl(object):
    dsl = {}
    es1 = False

    def __init__(self, es1=False):
        self.dsl = {}
        self.es1 = es1

    def to_dict(self):
        return self.dsl

    def buildFacetFilter(self, fociSelected):
        selected = {}
        for items in fociSelected:
            facet_name, foci_name = items.split(',')
            if facet_name not in selected:
                selected[facet_name] = []
            selected[facet_name].append(foci_name)

        filters = []

        for fa, foci in selected.items():
            musts = [{"term": {"facets.facet": fa}}]

            for fo in foci:
                musts.append({"term": {"facets.foci": [fo]}})
            facet = {"nested": {"path": "facets", "filter": {"bool": {"must": musts}}}}
            filters.append(facet)

        if self.es1:
            filter = {"and": {"filters": filters}}
        else:
            filter = {"bool": {"filters": filters}}
        return filter

    def buildPage(self, **kwargs):
        ctrl = {}
        if "size" in kwargs:
            ctrl["size"] = int(kwargs["size"])
            if "page" in kwargs:
                page = int(kwargs["page"]) - 1
                if page > 0:
                    ctrl["from"] = page * ctrl["size"]
        else:
            ctrl["size"] = 5000

        self.dsl.update(ctrl)

    def buildSort(self, **kwargs):
            sortmap = {"score": "_score", "popularity": "popularity", "date": "master.lastmodified"}
            sort = sortmap.get(kwargs.get("sort", "score"), "_score")
            order = kwargs.get("order", "desc")
            self.dsl.update({"sort":  [{sort: {"order": order}}]})

    def buildQuery(self, **kwargs):
        if "multi_match" in kwargs:
            match = {"multi_match": {"query": kwargs["multi_match"], "fields": kwargs["fields"]}}
        else:
            match = {"match_all": {}}    # todo this is just a placeholder need to do something real here

        if "facets" in kwargs:
            kwargs.setdefault("filter", []).append(self.buildFacetFilter(kwargs["facets"]))

        if "filter" in kwargs:
            if self.es1:
                query = {"query": {"filtered": {"query": match, "filter": kwargs["filter"]}}}
            else:
                query = {"query": {"bool": {"must": match, "filter": kwargs["filter"]}}}
        else:
            query = match
        self.dsl.update(query)

    def buildSuggest(self, data, source):
        self.dsl.update({"suggest": {"didyoumean": {"text": data, "term": {"field": source, "size": 10}}}})

    def aggFacets(self):
        self.dsl.update({"aggs":
                         {"nest":
                          {"nested":
                           {"path": "facets"},
                           "aggs": {"facetnames":
                                    {"terms":
                                     {"field": "facets.facet"},
                                     "aggs": {"focinames":
                                              {"terms": {"field": "facets.foci"}}
                                              }}}}}})


# TODO JP - need to put dict decodes inside try-except and return an appropriate error message if elasticsearch
# responce is not as expected. Currently error message is unhelpful.
class Esearch(object):
    def __init__(self, host,  control, token="",
                 oauth_token="", verify_ssl=True):
        self.host = host
        self.control = control

    def request(self, method, url, params=None, data=None, raw_response=False):
        """Makes requests to elasticsearch and returns result in json format"""
        kwargs = dict({}, **{
            'params': params or {},
            'headers': {},
            'data': data or {}
        })

        # note : elastic search takes a payload on
        # GET and delete requests - this is non standard
        if method in ('post', 'put', 'get', 'delete'):
            kwargs['data'] = json.dumps(data)  # ES vseems to not like unicode
            kwargs['headers']['Content-Type'] = 'application/json'

        response = getattr(requests, method)(url, **kwargs)
        # TODO check to see if all exceptions are being handled
        if response.status_code in (200, 201):
            if not response.content.strip():  # success but no response content
                return True
            try:
                return response.json()
            except (ValueError, TypeError):
                raise JSONDecodeError(response)

        elif response.status_code == 400:
            raise BadRequestError(response.text)
        elif response.status_code == 404:
            raise ResourceNotFoundError
        elif response.status_code == 409:
            raise ConflictError
        elif response.status_code == 412:
            raise PreconditionError
        elif response.status_code == 500:
            raise ServerError
        elif response.status_code == 503:
            raise ServiceUnreachableError
        raise UnknownError(response.status_code)

    def make_url(self, index, *args):
        url = urljoin(self.host, posixjoin(index, *args))
        return url

    # JP: TODO refactor this to use the smaller functions in the DSL class
    # JP: TODO refactor to make the queries between delivery and management more consistent
    def buildDsl(self, fields, **kwargs):
        # query = [{"match_all":{}}]
        query = []
        facets = []
        filter = []
        clusters = []
        # queries
        if "keywords" in kwargs:
            query.append({"terms": {"keywords": kwargs["keywords"],
                                    "minimum_should_match": "-0%"}})  # todo THINK ABOUT DOING MATCH PHRASE HERE
        if "title" in kwargs:
            query.append({"match": {"title": {"query": kwargs["title"], "operator": "and"}}})
        if "scope" in kwargs:
            query.append({"match": {"scope": {"query": kwargs["scope"], "operator": "and"}}})
        if "markup" in kwargs:
            query.append({"match": {"markup": {"query": kwargs["markup"], "operator": "and"}}})
        if "id" in kwargs:
            query.append({"match": {"id": {"query": kwargs["id"], "operator": "and"}}})

            # filters
        if "purpose" in kwargs:
            filter.append({"terms": {"purpose": kwargs["purpose"]}})

            # nested into clusters # TODO should this be a filter ?
        if "cluster" in kwargs:
            clusters.append({"term": {"clusters.cluster": kwargs["cluster"]}})
            filter.append({"nested": {"path": "clusters", "filter": {"bool": {"must": clusters}}}})

            # nested into facets
        if "facet" in kwargs:
            facets.append({"term": {"facets.facet": kwargs["facet"]}})
            if "focus" in kwargs:
                facets.append({"term": {"facets.foci": kwargs["focus"]}})
            facetFilter = {"nested": {"path": "facets", "filter": {"bool": {"must": facets}}}}
            filter.append(facetFilter)

        dsl = {"query": {"filtered": {
            "query": {"bool": {"should": query}},
            "filter": {"bool": {"must": filter}}
        }},
            "fields": fields,
            "size": 5000,
            "sort": "id"}

        return dsl


# JP: TODO think about whether to return whole ES response just the hits or something more generic
# query functions
    def search(self, index, type, dsl):
        url = self.make_url(index, type, "_search")
        r = self.request("get", url, data=dsl)
        return r

    def get_documents(self, type, **kwargs):
        fields = ["id", "title", "scope", "master.document", "master.version", "sensitivity", "purpose"]
        dsl = self.buildDsl(fields, **kwargs)
        r = self.search(kwargs["index"], type + "s", dsl)
        try:
            return r["hits"]
        except:
            raise ResultParseError

    def get_associate_list(self, index, aType):
        # JP TODO  this needs to be re-written as it no longe makes sense as associates are items !
        articles = []
        dsl = '{"query" : {"term":{ "type" : "' + aType + '" }},"fields":["id","title"],"size":"1000"}'
        res = self.search(index, "articles", dsl)
        for hit in res["hits"]["hits"]:
            articles.append(hit["fields"])
        return {"count": res["hits"]["total"], "articles": articles}

    def get_articles(self, index, **kwargs):
        r = self.get_documents("article", index=index, **kwargs)
        try:
            return r["hits"]
        except:
            raise ResultParseError

    def get_items(self, index, **kwargs):
        r = self.get_documents("item", index=index, **kwargs)
        try:
            return r["hits"]
        except:
            raise ResultParseError

    def get_snippets(self, index, **kwargs):
        r = self.get_documents("snippet", index=index, **kwargs)
        try:
            return r["hits"]
        except:
            raise ResultParseError

    def get_document(self, index, type, id):
        url = self.make_url(index, type + 's', id)
        res = self.request("get", url)
        try:
            return res["_source"]
        except:
            raise ResultParseError

    def get_control(self, item):
        url = self.make_url(self.control, item)
        res = self.request("get", url)
        try:
            return res["_source"][item]
        except:
            raise ResultParseError

    def put_control(self, item, control):
        url = self.make_url(self.control, item)
        if item in control:
            self.request("put", url, control)
        else:
            raise ValidationError

    # TODO test this as I've rewritten it
    def get_similar(self, index, keywords):
        articles = []
        # TODO simple approach - need to do something  better probablywork from article id rather than keyword list
        if (len(keywords) > 0):
            should = []
            for k in keywords:
                should.append({"term": {"keywords": k}})
            dsl = {"query": {"bool": {"should": should}}, "fields": ["id", "title", "scope"]}
            url = self.make_url(index, "articles", "_search")
            r = self.request("get", url, data=dsl)
            try:
                for hit in r["hits"]["hits"]:
                    articles.append(hit["fields"])
            except:
                ResultParseError
        return articles

    def get_cluster(self, index, id, size=100):

        dsl = {"query": {"nested": {"path": "clusters", "filter": {"term": {"cluster": id}}}},
               "fields": ["id", "title", "scope", "sensitivity"],
               "size": size,
               "sort": [{"clusters.priority": {"order": "asc", "nested_path": "clusters",
                                               "nested_filter": {"term": {"clusters.cluster": id}}}}]}

        url = self.make_url(index, 'articles', '_search')
        res = self.request("get", url, data=dsl)
        articles = []

        try:
            for hit in res["hits"]["hits"]:
                articles.append(hit["fields"])
        except:
            ResultParseError
        return articles

    def get_cluster_list(self, index, **kwargs):
        if "max" in kwargs:
            max = kwargs["max"]
        else:
            max = 10000

        dsl = {"size": "0",
               "aggs": {
                         "clusters": {
                            "nested": {"path": "clusters"},
                            "aggs":  {"clusters":
                                      {"terms":
                                       {"field": "clusters.cluster", "order": {"_term": "asc"}, "size": max},
                                       "aggs": {
                                                    "sens": {
                                                        "reverse_nested": {},
                                                        "aggs": {"sens": {"terms": {"field": "sensitivity"}}}
                                                    }
                                                }
                                       },
                                      "cluster_count": {"cardinality": {"field": "clusters.cluster"}}}
                            }
                        }
               }
        url = self.make_url(index, "articles", "_search")
        res = self.request("get", url, data=dsl)

        try:

            # note I need a ordered dict that contains a list of clusters and their attributes"
            cls = dict([(c["key"], {"id": c["key"], "count": c['doc_count'], "title": "_no landing page",
                                    "scope": "no landing page for cluster " + c["key"]}) for c in
                        res["aggregations"]["clusters"]["clusters"]["buckets"]])

            cls = dict([(c["key"], {"id": c["key"], "count":c['doc_count'], "title":"_no landing page",
                                    "scope":"no landing page for cluster " + c["key"],
                                    "sens":c["sens"]["sens"]["buckets"]}) for c in
                        res["aggregations"]["clusters"]["clusters"]["buckets"]])
        except:
            ResultParseError

        dsl = {"fields": ["id", "title", "scope"],
               "query": {"term": {"purpose": "landing"}},
               "sort": {"id": "asc"},
               "size": "2000"}

        url = self.make_url(index, "articles", "_search")

        res = self.request("get", url, data=dsl)

        try:
            cl = res["hits"]["hits"]
            for c in cl:
                cls[c["fields"]["id"][0]]["title"] = c["fields"]["title"][0]
                cls[c["fields"]["id"][0]]["scope"] = c["fields"]["scope"][0]
        except:
            ResultParseError

        return cls

    # editing stuff
    #
    def get_item_use(self, index, item):
        # dsl = {"fields": ["id"], "query": {"term": {"items.item": item}}, "size": 1000}  # es1.4
        dsl = {"stored_fields": ["id"], "query": {"term": {"items.item": item}}, "size": 1000}  # es5.2
        url = self.make_url(index, 'articles', '_search')
        deps = []
        res = self.request("get", url, data=dsl)
        try:
            for h in res["hits"]["hits"]:
                deps.append(h["fields"]["id"][0])
        except:
            ResultParseError
        return {"hits": deps}

    # publishing stuff
    #
    # clear index and set commit record to empty
    def clear_index(self, index):
        query = {"sort": {"seq": "desc"}, "size": "1"}
        url = self.make_url(index, "commits", "_search")
        r = self.request("post", url, data=query)["hits"]["hits"]
        if len(r) == 1:
            last = r[0]["_source"]
            seq = int(last["seq"]) + 1
        else:
            seq = 0
        up = {"seq": seq, "state": "complete", "newcommit": "empty"}
        url = self.make_url(index, "commits", "{0}-{1}".format(index, seq), "_update")
        self.request("post", url, data={"doc": up, "doc_as_upsert": "true"}, params={"refresh": "true"})
        self.del_km(index, "articles", "*")  # wildcard to delete all items but not the document mapping
        self.del_km(index, "items", "*")
        self.del_km(index, "snippets", "*")

    def post_log(self, index, seq, log):
        try:
            url = self.make_url(index, "commits", "{0}-{1}".format(index, seq)).strip()

            r = self.request("get", url)

            last = r["_source"]

            if last['state'] not in ['updating']:
                return
            up = {}
            up["log"] = last["log"]
            up["log"].append(log)
            url = self.make_url(url, "_update")
            self.request("post", url, data={"doc": up, "doc_as_upsert": "true"}, params={"refresh": "true"})
        except:
            pass

    def get_empty(self, channel):
            return {"seq": 0, "state": "complete", "newcommit": "empty"}

    def get_success(self, index):
        query = {"query": {
                    "filtered": {
                       "query": {
                        "match_all": {}},
                       "filter": {"term": {"state": "complete"}}
                        }
                    },
                 "sort": {"seq": "desc"},
                 "size": "1"}
        url = url = self.make_url(index, "commits", "_search")
        r = self.request("post", url, data=query)["hits"]["hits"]
        if len(r) == 0:
            return None
        else:
            return r[0]["_source"]

    def get_state(self, index, seq=None):
        if seq:
            url = self.make_url(index, "commits", "{0}-{1}".format(index, seq))
            r = self.request("get", url,)
            return r["_source"]
        else:
            query = {"sort": {"seq": "desc"}, "size": "1"}
            url = self.make_url(index, "commits", "_search")
            r = self.request("post", url, data=query)["hits"]["hits"]
            if len(r) == 0:
                return None
            else:
                return r[0]["_source"]

    def post_end(self, index, seq, newcommit, state, log=None):
        last = self.get_state(index)
        if not seq == last["seq"]:
            m = "Requested seq <{0}> does not match in progress seq <{1}>".format(seq, last["seq"])

            raise CommitError(m)
        elif not last["state"] == "updating":
            m = "Latest commit <{0}> in wrong state = {1}".format(last["seq"], last['state'])

            raise CommitError(m)
        elif not last["newcommit"] == newcommit:
            m = "Requested commit <{0}> does not match in progress commit <{1}>".format(newcommit, last["newcommit"])

            raise CommitError(m)
        else:
            up = {"finish": datetime.datetime.isoformat(datetime.datetime.now()), "state": state}
            # import pdb;pdb.set_trace()
            if log:
                up["log"] = [log]
            url = self.make_url(index, "commits", "{0}-{1}".format(index, seq), "_update")
            self.request("post", url, data={"doc": up, "doc_as_upsert": "true"}, params={"refresh": "true"})

    def reset_up(self, index, seq):
        url = self.make_url(index, "commits", "{0}-{1}".format(index, seq))
        self.request("delete", url)

    def post_up(self, index, last, newcommit):
        up = {}
        # start new commit
        seq = int(last["seq"]) + 1
        up["seq"] = seq
        up["start"] = datetime.datetime.isoformat(datetime.datetime.now())
        up["finish"] = datetime.datetime.isoformat(datetime.datetime.min)
        up["oldcommit"] = last["newcommit"]
        up["newcommit"] = newcommit
        up["state"] = "updating"
        up["log"] = ["updating from {0} to {1} ".format(up["oldcommit"], newcommit)]
        url = self.make_url(index, "commits", "{0}-{1}".format(index, seq), "_update")
        self.request("post", url, data={"doc": up, "doc_as_upsert": "true"}, params={"refresh": "true"})
        return up

    # POST to partially update or completetly create - not idempotent - not safe
    def post_km(self, index, oType, kmj, repl=False):
        try:
            id_value = kmj["id"]
        except:
            raise ValidationError("no id field in json structure")

        if repl:
            # create or update changed fields
            url = self.make_url(index, oType, id_value, "_update")
            # ES5 : True was unquoted changed this to "true"  - ES1 break ?
            doc = {"doc": kmj, "doc_as_upsert": "true"}
        else:
            # completely replace
            url = self.make_url(index, oType, id_value)
            doc = kmj
        self.request("post", url, data=doc)
        return ({"act": "replace" if repl else "update", "status": "200", "reason": "OK"})

    def del_km(self, index, oType, id=""):
        try:

            if (id == '*'):
                data = {"query": {
                    "match_all": {}}}  # note this is deprecated and cannot be done in v 2.0 onwards
                url = self.make_url(index, oType, "_query")
            else:
                data = {}
                url = self.make_url(index, oType, id)

            r = self.request("delete", url, data=data)
        except ResourceNotFoundError:
            r = requests.Response()
            r.status_code = 200
            r.reason = "Resource to be deleted did not exist <{0}>".format(url)
        return r


# setup stuff

    def put_mapping(self, index, mapping, force=False):
        url = self.make_url(index)
        if force:
            try:
                self.request("delete", url)
            except:
                pass
        self.request("put", url, data=mapping)

    def get_info(self):
        url = self.host
        return self.request("get", url)
