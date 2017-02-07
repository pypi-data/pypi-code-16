import json, sys

from everlastly import Everlastly

from private_settings.apikeys import pub_key, priv_key

print_positive, raise_on_errors = False, False
e=Everlastly(pub_key, priv_key)
uuids=[]

anchor_tests = [
 { 'arguments': {'hash': '1'*64, 'kwargs': {} }, 'success':True, 'error': None},
 { 'arguments': {'hash': '1'*64, 'kwargs': {'metadata':{"隨機詞":'👌'}} }, 'success':True, 'error': None},
 { 'arguments': {'hash': '1'*64, 'kwargs': {'metadata':{"隨機詞":'👌'}, 'save_dochash_in_receipt':True} }, 'success':True, 'error': None},
 { 'arguments': {'hash': '1'*64, 'kwargs': {'metadata':{"隨機詞":'👌'}, 'save_dochash_in_receipt':True, 'no_salt': True} }, 'success':True, 'error': None},
 { 'arguments': {'hash': '1'*64, 'kwargs': {'metadata':{"隨機詞":'👌'}, 'save_dochash_in_receipt':True, 'no_salt': True, 'no_nonce': True} }, 'success':True, 'error': None},
 { 'arguments': {'hash': '1'*63, 'kwargs': {} }, 'success':False, 'error': 'Wrong length of `hash` parameter\n'},
]

def run_tests():
  run_anchor_tests()
  run_get_receipts_tests()


def run_anchor_tests():
  for num,test in enumerate(anchor_tests):
    try:
      dochash = test['arguments']['hash']
      kwargs = test['arguments']['kwargs']
      success = test['success']
      error = test.get('error')
    except:
      raise ValueError("Bad formed test %s"%test)
    res = e.anchor(dochash, **kwargs)
    if res['success']!=success:
      if raise_on_errors:
        raise AssertionError("For test \n%s we got \n%s"%(json.dumps(test, indent=4), json.dumps(res, indent=4)))
      else:
        print("For test \n%s we got \n%s"%(json.dumps(test, indent=4), json.dumps(res, indent=4)))
    else:
      if (not res['success']) and (error!=res['error_message']):
        raise AssertionError("For test \n%s we got error `%s`, but expected `%s`"%(json.dumps(test, indent=4), res['error_message'], error))
      elif print_positive:
        print("👌OK\tAnchor test %d done correctly"%num)
    if res['success']:
      uuids.append(res['receiptID'])

def run_get_receipts_tests():
  receipt_list = ['Not token', 'eb6c398d-341c-4d3b-81f0-225958991a5f'] + uuids
  res = e.get_receipts(receipt_list)
  success=True
  assert(res['success'])
  bad_receipts, good_receipts = res['receipts'][:2], res['receipts'][2:]
  for ind,br in enumerate(bad_receipts):
    if not br['status']=="Error":
      txt="Problem with %d example: %s"%(ind, json.dumps(br, indent=4))
      success=False
      if raise_on_errors:
        raise AssertionError(txt)
      else:
        print(txt)
  for ind,gr in enumerate(good_receipts):
    if not gr['status']=="Success":
      txt = "Problem with %d example: %s"%(ind, json.dumps(gr, indent=4))
      success=False
      if raise_on_errors:
        raise AssertionError(txt)
      else:
        print(txt)
  if print_positive:
        print("👌OK\tGet_receipts test %d done correctly"%0)      
  
if __name__ == "__main__":
  print_positive = 'print_positive' in sys.argv
  raise_on_errors = 'raise_on_errors' in sys.argv
  run_tests()
