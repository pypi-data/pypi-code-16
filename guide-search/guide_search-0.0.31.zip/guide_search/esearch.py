import requests
import json
import datetime
from guide_search._version import __version__


try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
from posixpath import join as posixjoin

from guide_search.dsl import Dsl
from guide_search.exceptions import (
    JSONDecodeError,
    BadRequestError,
    ResourceNotFoundError,
    ConflictError,
    PreconditionError,
    ServerError,
    ElasticsearchError,
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


"""


# TODO JP - need to put dict decodes inside try-except and return an appropriate error message if elasticsearch
# responce is not as expected. Currently error message is unhelpful.
# TODO I need to think more about how to change the host after initialisation

class Esearch(object):

    def __init__(self, host,  control):
        self.init(host, control)

    def init(self, host, control):
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
            raise ElasticsearchError(response.text)
        elif response.status_code == 503:
            raise ServiceUnreachableError
        raise UnknownError(response.status_code)

    def make_url(self, index, *args):
        url = urljoin(self.host, posixjoin(index, *args))
        return url


# JP: TODO refactor this to use the smaller functions in the DSL class
# JP: TODO refactor to make the queries between delivery and management more consistent
    def buildDsl1(self, fields, **kwargs):
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
            filter.append({"nested": {"path": "clusters", "query": {"bool": {"must": clusters}}}})

            # nested into facets
        if "facet" in kwargs:
            facets.append({"term": {"facets.facet": kwargs["facet"]}})
            if "focus" in kwargs:
                facets.append({"term": {"facets.foci": kwargs["focus"]}})
            facetFilter = {"nested": {"path": "facets", "query": {"bool": {"must": facets}}}}
            filter.append(facetFilter)

        dsl = {"query": {"filtered": {
            "query": {"bool": {"should": query}},
            "filter": {"bool": {"must": filter}}
        }},
            "fields": fields,
            "size": 5000,
            "sort": "id"}
        return dsl

    def buildDsl(self, **kwargs):
        dsl = Dsl().match_all()

        if "_fields" in kwargs:
            dsl.fields(kwargs["_fields"])
        dsl.size('5000').sort('id')

        if "keywords" in kwargs:
            dsl.Q_should({"terms": {"keywords": kwargs["keywords"],
                                    "minimum_should_match": "-0%"}})  # todo THINK ABOUT DOING MATCH PHRASE HERE
        if "title" in kwargs:
            dsl.Q_should({"match": {"title": {"query": kwargs["title"], "operator": "and"}}})
        if "scope" in kwargs:
            dsl.Q_should({"match": {"scope": {"query": kwargs["scope"], "operator": "and"}}})
        if "markup" in kwargs:
            dsl.Q_should({"match": {"markup": {"query": kwargs["markup"], "operator": "and"}}})
        if "id" in kwargs:
            dsl.Q_should({"match": {"id": {"query": kwargs["id"], "operator": "and"}}})

            # filters
        if "purpose" in kwargs:
            dsl.Q_filter({"terms": {"purpose": kwargs["purpose"]}})

            # nested into clusters # TODO should this be a filter ?
        if "cluster" in kwargs:
            clusters = [{"term": {"clusters.cluster": kwargs["cluster"]}}]
            dsl.Q_filter({"nested": {"path": "clusters", "filter": {"bool": {"must": clusters}}}})

            # nested into facets
        if "facet" in kwargs:
            facets = [{"term": {"facets.facet": kwargs["facet"]}}]
            if "focus" in kwargs:
                facets.append({"term": {"facets.foci": kwargs["focus"]}})
            facetFilter = {"nested": {"path": "facets", "filter": {"bool": {"must": facets}}}}
            dsl.Q_filter(facetFilter)


        return dsl.dsl()


# JP: TODO think about whether to return whole ES response just the hits or something more generic
# query functions
    def search(self, index, type, dsl):
        url = self.make_url(index, type, "_search")
        r = self.request("get", url, data=dsl)
        return r

    def get_documents(self, index, type, **kwargs):
        dsl = self.buildDsl(**kwargs)
        r = self.search(index, type + "s", dsl)
        try:
            results = []
            for hit in r["hits"]["hits"]:
                results.append(hit["_source"])
            return results
        except:
            raise ResultParseError

    def get_associate_list(self, index, aType):
        # JP TODO  this needs to be re-written as it no longe makes sense as associates are items !
        articles = []
        dsl = Dsl().associate_list(aType).dsl()
        res = self.search(index, "articles", dsl)
        for hit in res["hits"]["hits"]:
            articles.append(hit["_source"])
        return {"count": res["hits"]["total"], "articles": articles}

    def get_articles(self, index, **kwargs):
        r = self.get_documents(index, "article", **kwargs)
        return r

    def get_items(self, index, **kwargs):
        r = self.get_documents(index, "item",  **kwargs)
        return r

    def get_snippets(self, index, **kwargs):
        r = self.get_documents(index, "snippet", **kwargs)
        return r

    def get_document(self, index, type, id):
        url = self.make_url(index, type + 's', id)
        res = self.request("get", url)
        try:
            return res["_source"]
        except:
            raise ResultParseError

    def get_control(self, id):
        url = self.make_url(self.control, id)
        res = self.request("get", url)
        try:
            return res["_source"][id]
        except:
            raise ResultParseError

    def get_similar(self, index, id):
        articles = []
        dsl = Dsl().more_like_this(index, id).size(5).dsl()
        url = self.make_url(index, "articles", "_search")
        r = self.request("get", url, data=dsl)
        try:
            for hit in r["hits"]["hits"]:
                articles.append(hit["_source"])
        except:
            ResultParseError
        return articles

    def get_cluster(self, index, id, size=100):
        dsl = Dsl().query_cluster(id).size(100).dsl()
        url = self.make_url(index, 'articles', '_search')
        res = self.request("get", url, data=dsl)
        articles = []

        try:
            for hit in res["hits"]["hits"]:
                articles.append(hit["_source"])
        except:
            ResultParseError
        return articles

    def get_cluster_list(self, index, **kwargs):
        if "max" in kwargs:
            max = kwargs["max"]
        else:
            max = 10000

        dsl = Dsl().cluster_list(max).dsl()
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

        dsl = Dsl().landing_list().size(max).dsl()
        url = self.make_url(index, "articles", "_search")

        res = self.request("get", url, data=dsl)

        try:
            cl = res["hits"]["hits"]
            for c in cl:
                cls[c["_source"]["id"]]["title"] = c["_source"]["title"]
                cls[c["_source"]["id"]]["scope"] = c["_source"]["scope"]
        except:
            ResultParseError

        return cls

    # editing stuff
    #
    def get_item_use(self, index, id):
        dsl = Dsl().item_use(id).dsl()
        url = self.make_url(index, 'articles', '_search')
        deps = []
        res = self.request("get", url, data=dsl)
        try:
            for hit in res["hits"]["hits"]:
                deps.append(hit["_source"]["id"])
        except:
            ResultParseError
        return deps

    # publishing stuff
    #
    # clear index and set commit record to empty
    def clear_index(self, index):
        query = Dsl().match_all().sort("seq", "desc").size("1")
        url = self.make_url(index, "commits", "_search")
        res = self.request("post", url, data=query.dsl())["hits"]["hits"]
        if len(res) == 1:
            last = res[0]["_source"]
            seq = int(last["seq"]) + 1
        else:
            seq = 0

        self.get_empty(index, seq)  # create a reference to empty then delete all content
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

    # TODO think about combining this with the clear function
    def get_empty(self, index, seq=0):
        up = {}
        # create a commit pointing to empty
        up["seq"] = seq
        up["start"] = datetime.datetime.isoformat(datetime.datetime.now())
        up["finish"] = up["start"]
        up["oldcommit"] = "empty"
        up["newcommit"] = "empty"
        up["state"] = "empty"
        up["log"] = ["no commit yet"]
        url = self.make_url(index, "commits", "{0}-{1}".format(index, up["seq"]))
        self.request("post", url, data=up)
        return up

    def get_last_success(self, index):
        # query = {"query": {
        #             "filtered": {
        #                "query": {
        #                 "match_all": {}},
        #                "filter": {"term": {"state": "complete"}}
        #                 }
        #             },
        #          "sort": {"seq": "desc"},
        #          "size": "1"}  # es1
        query = Dsl().match_all({"term": {"state": "complete"}}).sort("seq", "desc").size("1")
        url = url = self.make_url(index, "commits", "_search")
        # r = self.request("post", url, data=query)["hits"]["hits"] # es 1
        res = self.request("post", url, data=query.dsl())
        states = res["hits"]["hits"]
        if len(states) == 0:
            return self.get_empty(index)
        else:
            return states[0]["_source"]

    def get_state(self, index, seq=None):
        if seq:
            url = self.make_url(index, "commits", "{0}-{1}".format(index, seq))
            res = self.request("get", url,)
            return res["_source"]
        else:
            query = Dsl().match_all().sort("seq", "desc").size(1)
            url = self.make_url(index, "commits", "_search")
            res = self.request("post", url, data=query.dsl())
            states = res["hits"]["hits"]
            if len(states) == 0:
                return self.get_empty(index)
            else:
                return states[0]["_source"]

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
            # es 1
            # if (id == '*'):
            #     data = {"query": {
            #         "match_all": {}}}  # note this is deprecated and cannot be done in v 2.0 onwards
            #     url = self.make_url(index, oType, "_query")
            # else:
            #     data = {}
            #     url = self.make_url(index, oType, id)

            if (id == '*'):
                delete_query = Dsl().match_all()
                url = self.make_url(index, oType, "_delete_by_query")
                res = self.request("post", url, data=delete_query.dsl())
                # TODO read the documentation and handle error conditions.
            else:
                url = self.make_url(index, oType, id)
                res = self.request("delete", url)

        except ResourceNotFoundError:
            res = requests.Response()
            res.status_code = 200
            res.reason = "Resource to be deleted did not exist <{0}>".format(url)
        return res


# setup stuff
    def put_mapping(self, index, mapping, force=False):
        url = self.make_url(index)
        if force:
            try:
                self.request("delete", url)
            except:
                pass
        return self.request("put", url, data=mapping)

    def put_control(self, id, control):
        url = self.make_url(self.control, id)
        if id in control:
            self.request("put", url, data=control)
        else:
            raise ValidationError("url:{0}".format(url))

    def get_info(self):
        info = {"host": self.host,
                "control": self.control,
                "guide_search_version": __version__}
        try:
            url = self.host
            res = self.request("get", url)
            info["version"] = res["version"]["number"]
            info["name"] = res["name"]
            url = self.make_url("_cluster", "health")
            try:
                health = self.request("get", url)
                info["cluster_name"] = health["cluster_name"]
                info["cluster_health"] = health["status"]
                if health["status"] == "green":
                    info["status"] = "alive"
                else:
                    info["status"] = "limping"
            except:
                info["status"] = "not quite alive"
        except:
            info["status"] = "dead"
        return info

    def get_index_info(self, index):
        info = {}
        url = self.make_url(index, "articles", "_count")
        info.update({"articles": self.request("put", url)})
        url = self.make_url(index, "items", "_count")
        info.update({"items": self.request("put", url)})
        url = self.make_url(index, "snippets", "_count")
        info.update({"snippets": self.request("put", url)})
        return info
