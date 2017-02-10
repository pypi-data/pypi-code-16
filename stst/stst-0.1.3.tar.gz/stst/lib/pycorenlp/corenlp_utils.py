from corenlp import StanfordCoreNLP

class StanfordNLP:
    def __init__(self):
        self.server = StanfordCoreNLP('http://localhost:9000')

    def parse(self, text):
        output = self.server.annotate(text, properties={
            'timeout': '50000',
            'ssplit.isOneSentence': 'true',
            'annotators': 'tokenize,lemma,ssplit,pos,depparse,parse,ner',
            # 'annotators': 'tokenize,lemma,ssplit,pos,ner',
            'outputFormat': 'json'
        })

        return output

nlp = StanfordNLP()
