# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import boto3
import logging

#  한글 호출 문제 수정
reload( sys )
sys.setdefaultencoding( 'utf-8' )

# 로깅 설정
logger = logging.getLogger()
logger.setLevel( logging.INFO )


# S3 클라이언트
class S3OBJ :
    def tmp( self, path ) :
        """
        경로 앞에 tmp를 붙여줍니다.
        :param path: 
        :return: /tmp/<path>
        """
        p = path

        # 경로앞에 /tmp/가 있을경우 값을 그대로 반환합니다.
        if p[ :5 ] == '/tmp/' :
            return p
        elif p[ :4 ] == 'tmp/' :
            return "/{}".format( p )
        elif '/' == p[ 0 ] :
            # 경로 앞에 '/'이 있을경우 제거합니다.
            p = p[ 1 : ]

        return "/tmp/{}".format( p )

    def __init__( self, bucket, key, local_path=None ) :
        """
        s3오브젝트의 정보를 가져옵니다. 다운로드 위치를 지정할수 있습니다.
        :param bucket: 오브젝트가 위치한 버킷
        :param key: 오브젝트 키값
        :param local_path: 다운로드 받을 위치, 지정않할시 tmp/
        """
        self.local_path = local_path
        self.bucket = bucket
        self.key = key
        # 파일이 특정 폴더에 속하여 경로 앞에 '/'가 있을 경우 삭제
        if self.key[0] == '/':
            self.key = self.key[1:]

        # 객체 이름(확장자 포함)
        self.file = self.key.split( '/' )[ -1 ]

        # 객체이름에서 확장자와 이름 분리
        detail = self.file.split( '.' )
        # 확장자가 없는 파일일 경우
        if len( detail ) == 1 :
            self.extend = None
            self.name = self.file
        # 확장자가 있을 경우
        else :
            self.extend = detail[ -1 ]
            self.name = ''.join( detail[ :-1 ] )

        # 다운로드 경로가 존재하지 않을경우 /tmp/<파일명>을 다운로드 경로로 지정합니다.
        self.download_path = self.tmp( self.local_path ) if self.local_path else self.tmp( self.file )

    @property
    def check_download( self ) :
        # 파일 다운로드 여부 확인 메소드
        if os.path.exists( self.download_path ) :
            return True
        # 파일이 존재 하지 않을경우 다운로드 받지 않았다고 표시
        else :
            return False

    def down( self, local_path=None, fource=False ) :
        """
        s3객체를 다운로드 합니다. 저장할 파일경로를 지정하지 않을 경우 자동으로 tmp/파일명으로 저장됩니다.
        :param local_path: 저장할 파일의 경로입니다. 해당경로 맨앞에 자동의 tmp폴더를 붙여줍니다. ex) file_path == path/haha.mp3 일경우 tmp/path/haha.mp3에 다운로드 됩니다.
        :param fource: 이미 다운로드된 파일이 있더라도 다시 다운로드 합니다.
        :return: 
        """
        # 저장경로가 존재할경우 저장경로로 대체
        if local_path :
            self.download_path = self.tmp( local_path )

        # 이미 다운로드된 파일이 있고 강제 다운로드가 아닐경우 다운로드 하지 않는다.
        if self.check_download and not fource :
            pass
        else :
            logger.info( 'bucket: {0}, key: {1}, path: {2}'.format( self.bucket, self.key, self.download_path ) )
            boto3.client( 's3' ).download_file( self.bucket, self.key, self.download_path )
            logger.info( '{0} download'.format( self.download_path ) )
        return self.download_path

    def delet( self ) :
        # 용량관리를 위하여 다운로드 파일을 삭제합니다.
        if self.check_download :
            os.remove( self.download_path )
        else :
            pass


class EventOBJ( S3OBJ ) :
    """
    s3트리거로 전송받은 오브젝트 정보 추출 및 s3 객체 가져오기
    """

    def __init__( self, event ) :
        self.event = event
        self.obj_info()

    def obj_info( self ) :
        # S3이벤트 트리거에서 s3객체 정보를 가져와 S3OBJ객체를 생성합니다.

        # 이벤트 파라미터에서 s3정보만 가져온다.
        s3 = self.event[ 'Records' ][ 0 ][ 's3' ]
        bucket = s3[ 'bucket' ][ 'name' ]
        s3_obj = s3[ 'object' ]
        key = s3_obj[ 'key' ]
        # 파일 크기
        self.filesize = s3_obj[ 'size' ]
        S3OBJ.__init__( self, bucket, key )
