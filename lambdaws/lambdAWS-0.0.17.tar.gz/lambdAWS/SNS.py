# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import json
import logging

#  한글 호출 문제 수정
reload( sys )
sys.setdefaultencoding( 'utf-8' )

# 로깅 설정
logger = logging.getLogger()
logger.setLevel( logging.INFO )

from S3 import EventOBJ

# S3에서 SNS로 이벤트를 발행하면 SNS에 연결된 람다가 SNS메시지에서 S3메시지를 추출하고 이것을 이용하여 S3오브젝트를 가져온다.
class S3EVENT(EventOBJ):
    # SNS메시지에서 S3이벤트 메시지를 가져와 EventOBJ로 넘겨준다.
    def __init__(self, event):
        self.event = event
        s3msg = self.event['Records'][0]['Sns']['Message']
        s3event = json.loads(s3msg)
        logger.info('{}'.format(s3event))
        EventOBJ.__init__(self,s3event)