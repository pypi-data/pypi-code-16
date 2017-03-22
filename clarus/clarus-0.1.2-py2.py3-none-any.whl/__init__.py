#Name: clarus.py
#Runtimes: Python,Python_Lambda
#Leave blank line below to mark end of header

from __future__ import print_function
from six.moves import urllib
import requests
import json
import os
import sys
import logging

from clarus.services import *
from clarus.api_config import ApiConfig
from clarus.models import ApiResponse
from clarus.output_types import *
from clarus.api import request
#import urllib
# ------------------------------------------------------
# Params to be configured
# ------------------------------------------------------

API_ENV      = 'dev'                               # dev, rc, demo or eval

KEYDIRECTORY = 'C:/clarusft/keys/'                 # where to look for key files (else it looks in local directory)
KEYFILE      = 'API-Key.txt'
SECRETFILE   = 'API-Secret.txt'

# ------------------------------------------------------
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def openKey(file):
    if (os.path.isfile(KEYFILE)) :
        key = open(file).read()
    elif os.path.isdir(KEYDIRECTORY):
        key = open(KEYDIRECTORY+file).read()
    else:
        key = None
    return key
    
def kmsDecrypt(ciphertext):
    try:
        import boto3
        from base64 import b64decode 
        plaintext = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ciphertext))['Plaintext']
        return plaintext
    except:
        eprint ('decryption failed')
        logger.exception('Error decrypting ciphertext')
        return ciphertext

apiKey      = openKey(KEYFILE)
apiSecret   = openKey(SECRETFILE)

if apiKey is None:
    if 'CHARM_API_KEY' in os.environ:
        apiKey = os.environ['CHARM_API_KEY']
if apiSecret is None:
    if 'CHARM_API_SECRET' in os.environ:
        apiSecret = os.environ['CHARM_API_SECRET']
if (apiSecret is not None and len(apiSecret) > 40):
    apiSecret = kmsDecrypt(apiSecret)

# ------------------------------------------------------

TRADE_CCY   = 'TRADE'

FpML        = 'FpML'
headers     = {'Content-Type': 'application/json'}
API_URL     = '.api.clarusft.com/rest/v1/'
GRID_URL    = '.clarusft.com/rest/api/charm/Grid'

# Services

# COMPLIANCE_SERVICE  = 'Compliance'
# FRTB_SERVICE        = 'FRTB'
# HEDGE_SERVICE       = 'Hedge'
# MARGIN_SERVICE      = 'Margin'
# MARKET_SERVICE      = 'Market'
# PORTFOLIO_SERVICE   = 'Portfolio'
# PROFITLOSS_SERVICE  = 'ProfitLoss'
# RISK_SERVICE        = 'Risk'
# SDR_SERVICE         = 'SDR'
# SIMM_SERVICE        = 'SIMM'
TRADE_SERVICE       = 'Trade'
LOAD_SERVICE        = 'Upload'

XVA_SERVICE         = 'XVA'



#------------------------------------------------------------------------------------------------------

PrintURL           = False
PrintRequest       = False
PrintRequestTime   = True
PrintCalcTime      = False
PrintHTTPStatus    = False
#DefaultOutput      = TSV      

#------------------------------------------------------------------------------------------------------
# File handling

#------------------------------------------------------------------------------------------------------



