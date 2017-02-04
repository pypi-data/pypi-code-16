#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import requests

import relretrieval.app
from relretrieval.es.relretrieval_manager import SentenceManager, PatternManager


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", type=bool, default=False)
    args = parser.parse_args()

    # Check Elasticsearch
    es_endpoint = os.getenv("ELASTICSEARCH_URL")

    headers = {"Content-type": "application/json"}
    res = requests.get(es_endpoint, headers=headers)

    if res.status_code != 200:
        raise Exception("Somthing wrong with %s" % es_endpoint)

    es_version = res.json()["version"]["number"]

    print "Elasticsearch(%s) ENDPOINT : %s" % (es_version, es_endpoint)

    if args.init:

        print "Initializing ..."
        sentence_manager = SentenceManager(os.getenv("ELASTICSEARCH_URL"))
        try:
            sentence_manager.delete_index()
        except Exception as e:
            print e.message
        sentence_manager.create_index()
        sentence_manager.put_mapping()
        pattern_manager = PatternManager(os.getenv("ELASTICSEARCH_URL"))
        pattern_manager.put_mapping()
        print "done"

    else:

        # Check NER API Server
        ner_endpoint = os.getenv("NER_API_URL")

        headers = {"Content-type": "application/json"}
        res = requests.get(ner_endpoint + "/ner", headers=headers)

        if res.status_code != 200:
            raise Exception("Somthing wrong with %s" % ner_endpoint)

        res_json = res.json()

        status = res_json.get("status", None)

        if not status:
            raise Exception("Not satisfied NER API server")

        if status != "available":
            raise Exception("NER API Server is not available")

        print "NER API ENDPOINT : %s" % ner_endpoint

        relretrieval.app.run()
