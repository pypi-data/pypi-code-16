# encoding=utf-8
import pickle
import jieba
from gensim import corpora, models, similarities

class Counter:
    def __init__(self):
        self.dict = corpora.Dictionary.load('/Tmp/dd.dict')

    def count(self, sentence):
        seg_line = jieba.cut( sentence, cut_all=False)
        return len(self.dict.doc2bow(seg_line))
    def count_list(self,sentences):
        length = []
        for sentence in sentences:
            seg_line = jieba.cut( sentence, cut_all=False)
            number = len(self.dict.doc2bow(seg_line))
            length.append(number)
        return length

