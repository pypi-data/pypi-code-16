# -*- coding: utf-8 -*-

import os

from flask import Flask, request, jsonify
app = Flask(__name__)

setattr(app, "is_training", False)

from relretrieval.ner.tagger import NERTagger
from relretrieval.es.relretrieval_manager import SentenceManager, PatternManager
from relretrieval.BREDS.check import BREDS


@app.route("/")
def hello():
    res = jsonify(is_training=app.is_training)
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


@app.route("/docs", methods=["POST"])
def docs():
    print request.json

    try:
        text = request.json["text"]
        print text

        article_id = request.json.get("article_id", "")
        print article_id

        sentence_manager = SentenceManager(host=os.getenv("ELASTICSEARCH_URL"))
        # sentence_manager = SentenceManager()
        tagger = NERTagger(host=os.getenv("NER_API_URL"))

        tokens_list = tagger.apply([text])

        print tokens_list

        for order, tokens in enumerate(tokens_list):
            sentence = {}
            sentence["tokens"] = [{"token": tup[0]} for tup in tokens]
            sentence["article_id"] = article_id
            sentence["order"] = order
            sentence["entities"] = [{"token_index": token_index, "token": token[0], "label": token[1]}
                                    for token_index, token in enumerate(tokens) if token[1] != u"O"]

            print "saving sentence", sentence
            sentence_manager.save(sentence)

        res = jsonify(status="ok")
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res
    except Exception as e:
        print e.message
        res = jsonify(status="error", message=e.message)
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res


@app.route("/start", methods=["POST"])
def start():
    print request.json

    try:
        max_iter = request.json.get("max_iter", 10)
        print max_iter

        app.is_training = True

        # BREDS
        similarity = 0.0
        confidence = 0.0
        breads = BREDS(similarity, confidence)
        breads.generate_tuples()
        breads.init_bootstrap(tuples=None)

        app.is_training = False

        res = jsonify(status="ok", message="Training begins")
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res
    except Exception as e:
        print e.message
        res = jsonify(status="error", message=e.message)
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res


@app.route("/relations")
def relations():
    print request.args

    try:
        query = request.args.get("query", None)
        patters = []
        pattern_manager = PatternManager(host=os.getenv("ELASTICSEARCH_URL"))

        if not query:
            body = {
                "query": {"match_all": {}}
            }
            patters = pattern_manager.search(body)

        else:
            print query
            patters = pattern_manager.find_patters_by_query({"BEF": query})

        print patters

        res = jsonify(clusters=patters)
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res
    except Exception as e:
        print e.message
        res = jsonify(status="error", message=e.message)
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res


def run():
    app.run()
