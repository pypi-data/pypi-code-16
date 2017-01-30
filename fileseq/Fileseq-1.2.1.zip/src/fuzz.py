#!/usr/bin/env python

import fileseq 

def test_frameset(frange):
    try:    
        fs = fileseq.FrameSet(frange)
        frange2 = fileseq.framesToFrameRange(fs, sort=False)
        fs2 = fileseq.FrameSet(frange2)

    except fileseq.ParseException:
        return 

    assert fs == fs2
    assert fs.start() == fs2.start()
    assert fs.end() == fs2.end()
    assert fs.normalize() == fs2.normalize()


if __name__ == '__main__':
    import os
    import sys
    import afl
    afl.init()

    sample = sys.stdin.read()
    test_frameset(sample)
    
    os._exit(0)