#!/usr/bin/python
# coding: utf-8

import csv
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("../")
from common import log_tool

logger = log_tool.Logging.get_logger()

class DutExtractor(object):
    def __init__(self, dut_lib_file_path):
        self.word_dict = dict()
        self.negative_word_set = set()
        with open(dut_lib_file_path,'r') as f:
            reader = csv.reader(f)
            for item in reader:
                word = item[0].encode("UTF-8").strip()
                other = item[1:10]
                self.word_dict[word] = other

    def get_word_semantic(self, word_list):
        semantic_list = list()
        counter = 0
        while counter < len(word_list):
            word = word_list[counter].strip()
            word_semantic_dict = dict({"word":word})
            if self.word_dict.has_key(word):
                meaning = self.word_dict[word]
                kind = meaning[3]
                kind_meaning = self.get_kind_meaning(kind)
                word_semantic_dict["word_property"] = meaning[0]
                word_semantic_dict["word_meaning_count"] = meaning[1]
                word_semantic_dict["word_property_id"] = meaning[2]
                word_semantic_dict["kind"] = meaning[3]
                word_semantic_dict["meaning"] = kind_meaning
                word_semantic_dict["semantic_strength"] = meaning[4]
                word_semantic_dict["semantic_polagiry"] = meaning[5]
            semantic_list.append(word_semantic_dict)
            counter += 1
        return semantic_list

    def get_kind_meaning(self, kind):
        if kind == "PA":
            return "快乐"
        elif kind == "PE":
            return "安心"
        elif kind == "PD":
            return "尊敬"
        elif kind == "PH":
            return "赞扬"
        elif kind == "PG":
            return "相信"
        elif kind == "PB":
            return "喜爱"
        elif kind == "PK":
            return "祝愿"
        elif kind == "NA":
            return "愤怒"
        elif kind == "NB":
            return "悲伤"
        elif kind == "NJ":
            return "失望"
        elif kind == "NH":
            return "内疚"
        elif kind == "PF":
            return "思念"
        elif kind == "NI":
            return "慌张"
        elif kind == "NC":
            return "恐惧"
        elif kind == "NG":
            return "羞愧"
        elif kind == "NE":
            return "烦闷"
        elif kind == "ND":
            return "憎恶"
        elif kind == "NN":
            return "贬责"
        elif kind == "NK":
            return "妒忌"
        elif kind == "NL":
            return "怀疑"
        elif kind == "PC":
            return "惊奇"

if __name__ == '__main__':
    logger.debug("a")
    dut_extractor = DutExtractor("dut_sentiment_words.csv", "../common_lib/negative_words.txt")
    word_list = list()
    final_word_list = list()
    sentence = sys.argv[1].strip()
    length = len(sentence)
    bit_length = length / 3
    counter = 0
    while counter <= bit_length:
        word_list.append(str(sentence[(counter*3):(counter*3)+3]))
        if (counter + 1) * 3 < length:
            word_list.append(str(sentence[(counter*3):((counter+1)*3)+3]))
        if (counter + 2) * 3 < length:
            word_list.append(str(sentence[(counter*3):((counter+2)*3)+3]))
        if (counter + 3) * 3 < length:
            word_list.append(str(sentence[(counter*3):((counter+3)*3)+3]))
        counter += 1
    for item in word_list:
        item = item.encode("UTF-8")
        final_word_list.append(item)
    result_list = dut_extractor.get_word_semantic(final_word_list)
    for item in result_list:
        if item.has_key("meaning"):
            print item["word"], item
        else:
            print item["word"], item
