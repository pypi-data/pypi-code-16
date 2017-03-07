
from SeasObjects.model.Message import Message
from SeasObjects.model.Activity import Activity
from SeasObjects.model.Input import Input
from SeasObjects.model.SystemOfInterest import SystemOfInterest
from SeasObjects.model.Parameter import Parameter
from SeasObjects.rdf.Variant import Variant

from SeasObjects.factory.Factory import Factory
from SeasObjects.factory.RequestFactory import RequestFactory
from SeasObjects.common.HttpClient import HttpClient
from SeasObjects.common.HttpMessage import HttpMessage, parseMIMEmessage
from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.Tools import Tools
from SeasObjects.common.SeasCrypto import SeasCrypto
from SeasObjects.common.CryptoKeyWallet import CryptoKeyWallet
from SeasObjects.common.SERIALIZATION import SERIALIZATION

import traceback
import uuid
from SeasObjects.model.Transaction import Transaction

class TransactionAgent(object):
   
    transactionServerAddress = "http://development.asema.com:8088/app-core/transactionserver"
    messageIdCounter = 0
    transactionIdentifierUriPrefix = ""

    def __init__(self, transactionIdentifier):
        self.transactionIdentifierUriPrefix = transactionIdentifier
    
    @classmethod    
    def getDefaultNotary(cls):    
        return cls.transactionServerAddress
    
    @classmethod
    def sendKeyToNotary(cls, senderId, referenceId, hash, key, signature, notary):
        # first create Transaction Object
        keyTransferTransaction = None
        try:
            keyTransferTransaction = Factory.createTransaction(referenceId, senderId)
        except:
            traceback.print_exc()
            return False
                
        keyTransferTransaction.setSigner(senderId)
        message = Message()
        message.setHashCode(hash);
        message.setSignature(signature);
        message.setSessionKey(key);        
        keyTransferTransaction.setMessage(message)
        # then send to server to store
        return cls.storeToTransactionServer(senderId, notary, keyTransferTransaction)
    
    @classmethod
    def storeToTransactionServer(cls, senderId, notary, *args ):
        '''
        @param senderId: URI string
        @param notary: URI string
        @param args: a variable number of Transaction Objects  
        @return a boolean value
        '''
        try:
            client = HttpClient()
            # create an empty MIME multipart message
            sentHttpMessage = HttpMessage()
            
            # construct Request object
            req =  RequestFactory().create(senderId)
            req.setMethod(RESOURCE.WRITE)
            cls.messageIdCounter = cls.messageIdCounter+1
            req.setMessageId(cls.messageIdCounter)
            a = Activity()
            req.addActivity(a)
            i = Input()
            a.addInput(i)
            system = SystemOfInterest()
            system.setSameAs(notary)
            i.setSystemOfInterest(system)
            
            param = Parameter()
            param.setKey("transactions")
            param.setName("Transaction id list")
            param.setDescription("List of ids of transactions that are sent for storing into the database.")
            
            for transaction in args:
                param.addValue(transaction.getSeasIdentifierUri())
            i.addParameter(param)
            
            # save Request object to multipart message, Main part
            mainRequestString = Tools.toString(req)
            sentHttpMessage.addMainpart(mainRequestString)
            
            mainRequestHash = SeasCrypto().createEncodedMessageDigest(mainRequestString)
            requestSignature = SeasCrypto().sign(CryptoKeyWallet.getPrivateKey(), mainRequestHash)
            
            # create transaction for the main request                        
            if cls.transactionIdentifierUriPrefix=='':
                transactionIdentifierUri = senderId + uuid.uuid4().get_hex()
            else:
                transactionIdentifierUri = transactionIdentifierUri + uuid.uuid4().get_hex()
            requestTransaction = Factory.createTransaction(transactionIdentifierUri, senderId)    
            requestTransaction.setSigner(senderId)
            requestTransactionMessage = Message()
            requestTransactionMessage.setMessageId(req.getMessageId());
            requestTransactionMessage.setHashCode(mainRequestHash)
            requestTransactionMessage.setSignature(requestSignature)
            requestTransaction.setMessage(requestTransactionMessage)
            
            # save requestTransaction to multipart message, non-Main part
            requestTransactionString = Tools.toString(requestTransaction)
            sentHttpMessage.add(transactionIdentifierUri, requestTransactionString)
            
            # save transactions that are sent to multipart message, non-Main part
            for trans in args:                
                sentHttpMessage.add(trans.getSeasIdentifierUri(), Tools.toString(trans))
            
            # send out this multipart message  
            payload = removeFrontHeader(sentHttpMessage.asString())    
            #print '*** sent ****'
            #print payload
            #print '*************'                        
            resp, contentType = client.sendPost(notary, payload, sentHttpMessage.getContentType())
            #print "----response -----"
            #print resp
            return True
            
        except:
            traceback.print_exc()    
            return False
    
    @classmethod
    def fetchFromTransactionServer(cls, senderId, notary, *args):
        '''
        @param senderId: URI string
        @param notary: URI string
        @param args: a variable number of Transaction Objects  
        
        @return a dictionary, key is SeasIdentifierUri of each transaction, value is Transaction Object
        '''
        try:
            client = HttpClient()
            # create an empty MIME multipart message
            sentHttpMessage = HttpMessage()
            # main request
            req =  RequestFactory().create(senderId)
            req.setMethod(RESOURCE.READ)
            cls.messageIdCounter = cls.messageIdCounter+1
            req.setMessageId(cls.messageIdCounter)
            a = Activity()
            req.addActivity(a)
            i = Input()
            a.addInput(i)
            system = SystemOfInterest()
            system.setSameAs(notary)
            i.setSystemOfInterest(system)
            
            param = Parameter()
            param.setKey("transactions")
            param.setName("Transaction id list")
            param.setDescription("List of ids of transactions that are sent to be fetched the database.")
            
            for transaction in args:
                param.addValue(transaction.getSeasIdentifierUri())
            i.addParameter(param)
            
            # save Request object to multipart message, Main part
            mainRequestString = Tools.toString(req)
            sentHttpMessage.addMainpart(mainRequestString)
            
            mainRequestHash = SeasCrypto().createEncodedMessageDigest(mainRequestString)
            requestSignature = SeasCrypto().sign(CryptoKeyWallet.getPrivateKey(), mainRequestHash)
            
            #create transaction for the main request                        
            if cls.transactionIdentifierUriPrefix=='':
                transactionIdentifierUri = senderId + uuid.uuid4().get_hex()
            else:
                transactionIdentifierUri = transactionIdentifierUri + uuid.uuid4().get_hex()
            requestTransaction = Factory.createTransaction(transactionIdentifierUri, senderId)    
            requestTransaction.setSigner(senderId)
            requestTransactionMessage = Message()
            requestTransactionMessage.setMessageId(req.getMessageId());
            requestTransactionMessage.setHashCode(mainRequestHash)
            requestTransactionMessage.setSignature(requestSignature)
            requestTransaction.setMessage(requestTransactionMessage)
            
            # add requestTransaction to multipart message, non-Main part
            requestTransactionString = Tools.toString(requestTransaction)
            sentHttpMessage.add(transactionIdentifierUri, requestTransactionString)
            
            # add transactions that are sent to multipart message, non-Main part
            for trans in args:                
                sentHttpMessage.add(trans.getSeasIdentifierUri(), Tools.toString(trans))
            
            # send out this multipart message  
            payload = removeFrontHeader(sentHttpMessage.asString())    
            resp, contentType = client.sendPost(notary, payload, sentHttpMessage.getContentType())
            #print "----response -----"
            #print resp
            #print '--------content-type  ------------'
            #print contentType
            
            receivedHttpMessagestr = addFrontHeader(resp, contentType)
            receivedHttpMessage = parseMIMEmessage(receivedHttpMessagestr)
            
            map = {}
            non_main_parts_dict = receivedHttpMessage.getNonMainPartsAsDict() 
            counter = 0
            for part in non_main_parts_dict.values():               
                print '[received non_Main part ', counter, ': ]\n', part, '\n'
                counter = counter+1 
                # recover the part from string to Seas Obj
                model = Tools().fromString(part, SERIALIZATION.TURTLE)
                rootRes = Tools().getTopNode(model)[0]
                seasCls = Tools().getResourceClass(rootRes)
                recoveredObj =  seasCls.parse(rootRes)
                
                if isinstance(recoveredObj, Transaction): # We want to save the Transaction that hold the requested data
                    map[recoveredObj.getSeasIdentifierUri()] = recoveredObj            
            
            return map
        
        except:
            traceback.print_exc()  
    
    @classmethod
    def fetchKeyFromNotary(cls, senderId, referenceId, hash, signature, notary):
        '''
        @type senderId, referenceId, hash, signature, notary: all strings 
        @return: the fetched session Key as string
        '''
        transaction = None
        try:
            transaction = Factory.createTransaction(referenceId, senderId)
        except:
            traceback.print_exc()
            return None
        
        transaction.setSigner(senderId)
        message = Message()
        message.setHashCode(hash)
        message.setSignature(signature)
        transaction.setMessage(message)
                
        map = cls.fetchFromTransactionServer(senderId, notary, transaction)        
        transFound = map.get(referenceId)
        if transFound is None:
            print 'Requested transaction can not be found from notary!'
        else:
            return transFound.getMessage().getSessionKey()
           
    
def removeFrontHeader(httpMsgBody):
    '''
    Transaction server requires the MIME multipart body without Content-Type header,
    so I remove the header
    @return the bodyparts of multipart message, without headers
    '''
    ContentTypeHeader, payload = httpMsgBody.split('\n\n', 1)
    return payload
    
def addFrontHeader(body, contentType):  
    '''
    The opposite of removeFrontHeader() method. It adds content-type header in front
    of body, making the complete MIME multipart message.
    
    @return the complete MIME mutlipart message string, ready for HttpMessage.py to parse
    
    ''' 
    
    return 'Content-Type: '+ contentType+ '\n\n'+ body
    
                