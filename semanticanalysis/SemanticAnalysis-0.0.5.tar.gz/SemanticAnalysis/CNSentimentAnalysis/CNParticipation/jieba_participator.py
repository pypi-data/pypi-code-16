#!/usr/bin/python
#encoding=utf-8
import jieba

class JiebaParticipator(object):
    @staticmethod
    def participate(setence):
        seg_list = jieba.cut(setence, cut_all = False)
        return seg_list

if __name__ == '__main__':
    seg_list = JiebaParticipator.participate("今天的电影很不好看,看的非常不开心。你呢？怎么样？")
    for item in seg_list:
        print item
