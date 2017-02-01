# -*- coding: utf-8 -*-

import os

from flask import Flask, request, jsonify
app = Flask(__name__)

setattr(app, "is_training", False)

from relretrieval.ner.tagger import NERTagger
from relretrieval.es.relretrieval_manager import SentenceManager


@app.route("/")
def hello():
    return jsonify(is_training=app.is_training)


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

        return jsonify(status="ok")
    except Exception as e:
        print e.message
        return jsonify(status="error", message=e.message)


@app.route("/start", methods=["POST"])
def start():
    print request.json

    try:
        max_iter = request.json.get("max_iter", 10)
        print max_iter

        app.is_training = True

        # TODO
        # BREADS で学習

        # app.is_training = False

        return jsonify(status="ok", message="Training begins")
    except Exception as e:
        print e.message
        return jsonify(status="error", message=e.message)


@app.route("/relations")
def relations():
    print request.args

    try:
        query = rrequest.args.get("query", None)
        if not query:
            raise Exception("parameters not includes query")

        # TODO
        # query から検索

        return jsonify(status="ok")
    except Exception as e:
        print e.message
        return jsonify(status="error", message=e.message)


def run():
    app.run()
