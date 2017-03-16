#!/usr/bin/python
from dut_extractor import DutExtractor
import thread

lock = thread.allocate_lock()

class DutExtractorFactory(object):
    single_dut_extractor = None

    @staticmethod
    def get_dut_extractor(input_file):
        if DutExtractorFactory.single_dut_extractor is None:
            lock.acquire()
            if DutExtractorFactory.single_dut_extractor is None:
                DutExtractorFactory.single_dut_extractor = DutExtractor(input_file)
            lock.release()
        return DutExtractorFactory.single_dut_extractor

if __name__ == "__main__":
    dut_ext = DutExtractorFactory.get_dut_extractor("dut_sentiment_words.csv", "../common_lib/negative_words.txt")
    print dut_ext
