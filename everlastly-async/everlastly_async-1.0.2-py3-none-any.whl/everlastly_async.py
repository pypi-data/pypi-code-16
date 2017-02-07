#!/usr/bin/env python
# coding=utf-8

# everlastly.py: Everlastly API implementation
#
# Copyright © 2016 Emelyanenko Kirill
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import aiohttp
#from requests.exceptions import RequestException
from aiohttp.errors import __all__ as aiohttpException
from aiohttp.errors import *
import hmac
import json
from hashlib import sha512
from time import time
from urllib.parse import urlencode

class EverlastlyServerProblem(Exception):
    pass
class EverlastlyRequestProblem(Exception):
    pass

NetworkException=[]
for exception in aiohttpException:
  NetworkException.append(vars()[exception])
NetworkException=tuple(NetworkException)

class Everlastly:
    def __init__(self, loop, public_key, private_key):
        self.public_key  = public_key
        self.private_key = private_key
        self.loop = loop
        self.last_used_nonce = 0
        self.root_url = "https://everlastly.com/api/v1/"

    def next_nonce(self):
        self.last_used_nonce = max(time(),self.last_used_nonce+0.0001)
        return self.last_used_nonce

    async def _send_request(self, method, payload, test=False):
        payload_str = urlencode(payload)
        sign = hmac.new(bytes(self.private_key,'ascii') , bytes(payload_str,'ascii'), sha512).hexdigest() 
        headers = {'content-type': 'application/x-www-form-urlencoded', 'pub-key':self.public_key, 'sign':sign}
        if test:
          headers.update({'test':'True'})
        try:
          async with aiohttp.ClientSession(loop=self.loop) as session:
            async with session.post(self.root_url+method, data=payload_str, headers=headers) as resp:
              response = await resp.text() # We dont use .json() method 'cause server gives wrong mimetype  
              return json.loads(response)
        except json.decoder.JSONDecodeError as e:
          raise EverlastlyServerProblem("Strange answer from server %s"%request.text)

    # Get dochash and options and return dictionary { 'success': True/False, 'error_message': None/error_message, "receiptID": receiptID/None }
    async def anchor(self, dochash, metadata=None, test=False, save_dochash_in_receipt=False, no_salt=False, no_nonce=False, nonce=None):
        payload = {'hash':dochash}
        if not no_nonce:
          payload["nonce"]= nonce if nonce else self.next_nonce()
        else:
          payload["no_nonce"]='True'
        if metadata:
          payload["metadata"]=json.dumps(metadata)
        if no_salt:
          payload["no_salt"]='True'
        if save_dochash_in_receipt:
          payload["save_dochash_in_receipt"]='True'
        result={}
        try:
          response = await self._send_request('anchor', payload, test=test)
          if not "status" in response:
            raise EverlastlyServerProblem("No status in response")
          try:
            result["success"]= (response["status"]=="Accepted")
            result["error_message"]=None if response["status"]=="Accepted" else response["error"]
            result["receiptID"]=response["receiptID"] if response["status"]=="Accepted" else None
          except KeyError:
            raise EverlastlyServerProblem("Incomplete server response")
        except (EverlastlyServerProblem) as e:
          result["success"]=False
          result["error_message"]=e
          result["receiptID"]=None
        except NetworkException as e:
          result["success"]=False
          result["error_message"] = "Problem with network"+str(e)
          result["receiptID"]=None
        return result


    # Get list of receiptIDs and return dictionary {'success': True/False, 'error_message': None/error_message, 'receipts': [...]}
    # each element of receipts array is dictionary with fields:
    # status - status of this uuid request - 'Error'/'Success'
    # error_message - error_message/None
    # state - state of receipt - None/ ['confirmed', 'semiconfirmed', 'unconfirmed' or 'unfinished']
    # receipt - None/receipt_dictionary
    async def get_receipts(self, receipt_list, no_nonce=False, test=False, nonce=None):
        payload={'uuids':json.dumps(receipt_list)}
        if not no_nonce:
          payload["nonce"]= nonce if nonce else self.next_nonce()
        result={}
        try:
          response = await self._send_request('get_receipts', payload, test=test)
          if not "status" in response:
            raise EverlastlyServerProblem("No status in response")
          try:
            result["success"]=(response["status"]=="Succeed")
            result["error_message"]=None if response["status"]=="Succeed" else response["error"]
            result["receipts"]=response["receipts"] if response["status"]=="Succeed" else None
          except KeyError:
            raise EverlastlyServerProblem("Incomplete server response")
        except (EverlastlyServerProblem) as e:
          result["success"]=False
          result["error_message"]=e
          result["receipts"]=None
        except RequestException as e:
          result["success"]=False
          result["error_message"] = "Problem with network "+str(e)
          result["receipts"]=None
        return result
        
        

