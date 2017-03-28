# -*- coding: utf-8 -*-
import unittest
import json
import sys

#  한글 호출 문제 수정
reload( sys )
sys.setdefaultencoding( 'utf-8' )

from S3 import *


bucket = 'testbucket'
key = 'abc.mp3'

obj1 = S3OBJ(bucket,key)

path = '/tmp/{}'.format('sample.mp3')

class MyTestCase( unittest.TestCase ) :

    def test_tmp1( self ) :
        # 파일명
        self.assertEqual( obj1.tmp('sample.mp3'), path )

    def test_tmp2( self ) :
        # /파일명
        self.assertEqual( obj1.tmp( '/sample.mp3' ), path )

    def test_tmp3( self ) :
        # tmp/파일명
        self.assertEqual( obj1.tmp( 'tmp/sample.mp3' ), path )

    def test_tmp4( self ) :
        # /tmp/파일명
        self.assertEqual( obj1.tmp( '/tmp/sample.mp3' ), path )

    def EVENTOBJ(self):
        # 테스트용 s3 트리거 이벤트 메시지
        with open( 'event/s3.json' ) as msg :
            event = json.load( msg )
        pass

if __name__ == '__main__' :
    unittest.main()
