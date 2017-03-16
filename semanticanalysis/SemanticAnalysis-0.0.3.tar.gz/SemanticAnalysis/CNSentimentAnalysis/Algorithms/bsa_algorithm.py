#!/usr/bin/python
#encoding=utf-8
from algorithm import Algorithm

class BsaAlgorithm(Algorithm):
    def __init__(self, negative_word_file):
        negative_word_file = file(negative_word_file, "r")
        lines = negative_word_file.readlines()
        self.negative_word_set = set()
        for line in lines:
            line = line.encode("UTF-8").strip()
            if line.isspace():
                continue
            self.negative_word_set.add(line)
        negative_word_file.close()

    def cal_semantic_value(self, article_semantic_result):
        segment_value_list = list()
        for seg_result in article_semantic_result:
            seg_value = list()
            for setence_result in seg_result:
                setence_value = 0
                word_counter = 0
                for word_result in setence_result:
                    if word_result.has_key("meaning") is False:
                        word_counter += 1
                        continue
                    value = int(word_result["semantic_strength"])

                    # TODO check the polarity use the self negative word set, and change the polarity
                    last_word_pos = word_counter - 1
                    is_reverted = False
                    if last_word_pos >= 0:
                        last_word_result = setence_result[last_word_pos]
                        last_word = last_word_result["word"]
                        if last_word in self.negative_word_set:
                            is_reverted = True

                    if word_result["semantic_polagiry"] == "2":
                        value = value * (-1)
                    if is_reverted:
                        value = value * (-1)

                    setence_value += value
                    word_counter += 1
                seg_value.append(setence_value)
            segment_value_list.append(seg_value)
        segment_value = list()
        for item in segment_value_list:
            sum = 0
            counter = 0
            for value in item:
                sum += value
                counter += 1
            if counter == 0:
                average = 0
            else:
                average = sum /counter
            segment_value.append(average)
        article_sum = 0
        seg_counter = 0
        for seg in segment_value:
            article_sum += seg
            seg_counter += 1
        if seg_counter == 0:
            article_average = 0
        else:
            article_average = float(article_sum) / seg_counter
        # TODO add more result
        return article_average

