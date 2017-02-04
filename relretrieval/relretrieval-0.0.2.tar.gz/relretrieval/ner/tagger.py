# -*- coding: utf-8 -*-


import requests
import json


class NERTagger():

    def __init__(self, host="http://localhost:9000"):
        self.host = host
        res = requests.get(self.host + "/ner").json()
        if (res["status"] != "available"):
            raise Exception("Something wrong with %s" % host)

    def apply(self, sentences):

        tokens_list = []

        for sentence in sentences:
            token_tuples = self.tag_sent(sentence)
            token_tuples = self.combine_same_label(token_tuples)
            token_tuples = [self.space_to_plus(token_tuple) for token_tuple in token_tuples]
            tokens_list.append(token_tuples)

        return tokens_list

    def tag_sent(self, sentence):
        headers = {"Content-type": "application/json"}
        payload = {"text": sentence}
        res = requests.post(self.host + "/ner",
                            headers=headers,
                            data=json.dumps(payload))

        if res.status_code != 200:

            err_msg = ""
            err_msg += "RESPONSE\n"
            err_msg += "STATUS CODE:{}\n".format(res.status_code)
            err_msg += "HEADERS:{}\n".format(res.headers)
            err_msg += "{}\n".format(res.text)
            raise Exception(err_msg)

        tokens = res.json()["tokens"]
        return [(token["text"], token["label"]) for token in tokens]

    def combine_same_label(self, tokens):
        if len(tokens) == 0:
            return []

        WORD = 0
        LABEL = 1
        group_flags = [True
                       if tokens[i][LABEL] != u"O" and tokens[i][LABEL] == tokens[i + 1][LABEL]
                       else False
                       for i in range(len(tokens) - 1)]
        group_flags.append(False)

        grouped = []
        stack = []
        for i, group_flag in enumerate(group_flags):
            stack.append(tokens[i])
            if not group_flag:
                grouped.append(stack)
                stack = []

        return [(" ".join([item[0] for item in items]), items[0][1]) for items in grouped]

    def space_to_plus(self, token):
        encoded = token[0].replace(u"+", u"\+").replace(u" ", u"+")
        return (encoded, token[1])
