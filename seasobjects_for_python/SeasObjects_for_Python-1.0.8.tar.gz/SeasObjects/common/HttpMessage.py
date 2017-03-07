from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import email
from email.iterators import _structure


class HttpMessage(object):
    '''
    generate and parse message in MIME multipart/related (RFC2387) structure.
    Its core variable is a MIMEMultipart Object
    '''
    DEFAULT_MAIN_CONTENT_ID_HEADER_VALUE = 'Main'

    def __init__(self, multipart = None):
        '''
        If parameter 'multipart' is None, then create an empty MIMEMultipart, whose body parts
        need to be added by invoking methods addMainpart() and add().
        Otherwise reuse the exising multipart Object (this has been used by parseMIMEmessage() method.)
        '''
        if multipart==None:
            self.multipart = MIMEMultipart('related')  
        else:
            self.multipart = multipart                 
         
    def addMainpart(self, mainPartString, mainPartContentType='text/turtle'):  
        self.multipart.set_param('type', mainPartContentType)
        self.multipart.set_param('start', self.DEFAULT_MAIN_CONTENT_ID_HEADER_VALUE)
        
        self.add(self.DEFAULT_MAIN_CONTENT_ID_HEADER_VALUE, mainPartString, mainPartContentType) 
    
    def add(self, partId, partString, partContentType='text/turtle'):  
        [mainType, subType]=partContentType.split('/')  
        if mainType.lower()=='text':
            part = MIMEText(partString, subType)
        elif mainType.lower() == 'application':
            part = MIMEApplication(partString, subType)
        
        if part is not None:        
            part.add_header('Content-ID', partId)
            #mime package automatically add 'Content-Transfer-Encoding' header. We do not need it.
            #part.__delitem__('Content-Transfer-Encoding')
            self.multipart.attach(part)
                           
    def getBody(self):
        '''
        print out the whole multipart message as a String (including Content-Type header)
        @return string
        '''       
        #print '\n        < whole message starts ------>:'
        #print self.multipart.as_string()
        #print '        <whole message ends ------>\n'
        
        return self.multipart.as_string()     
         
    def getParts(self):  
        '''
        return the body parts as a list of MIME Object. Each body part includes body string and headers
        '''
        payload = self.multipart.get_payload()
        
        #for part in payload:
            #print part.__str__() # including body part string and headers
            #print part.get('Content-ID')
            #print part.get_payload() # body part string only
        
        return payload   
        
    
    def getPart(self, partId):
        '''
        return the body part whose Content-ID value is partId. Return only the body part string, no headers
        @return: string
        '''
        payload = self.multipart.get_payload()
        for part in payload:
            if partId == part.get('Content-ID'):
                return part.get_payload()
        
        return None
    
    def getMainPart(self):
        '''
        return the body part of "Main" part. No headers.
        '''
        return self.getPart(self.DEFAULT_MAIN_CONTENT_ID_HEADER_VALUE)
    
    def getNonMainPartsAsDict(self):
        '''
        return all those non "Main" parts as a dictionary (key is Content-ID, value is the body string). No headers
        '''
        rt = {}
        payload = self.multipart.get_payload()
        for part in payload:
            if part.get('Content-ID')!= self.DEFAULT_MAIN_CONTENT_ID_HEADER_VALUE:
                rt[part.get('Content-ID')] = part.get_payload()
                
        return rt                        
    
    def getContentType(self):
        '''
        return the Content-Type header value, including its parameters.
        '''
        return self.multipart.get('Content-Type')
           
    
    def isMultipart(self):
        return self.multipart.is_multipart()
    
    def asString(self):
        return self.getBody()


class HttpMessageSingle(object):
    '''
    generate and parse single part message in MIME structure.
    Its core variable is a MIMEmsg Object
    '''
    def __init__(self, singlePart = None):
        if singlePart is not None:
            self.singlePart = singlePart
        else:
            self.singlePart = None
            
    def add(self, contentString, contentType):
        '''
        This method only call once, for adding the single part message body
        
        @type both parameters are string. 
        '''
        [mainType, subType]=contentType.split('/')
        if mainType.lower()=='text':
            self.singlePart = MIMEText(contentString, subType)
        elif mainType.lower() == 'application':
            self.singlePart = MIMEApplication(contentString, subType)
               
    def asString(self):
        '''
        print out the whole single part message as a String (including Content-Type header)
        @return string
        '''                
        #print '\n        < whole message starts ------>:'
        #print self.singlePart.as_string()
        #print '        <whole message ends ------>\n'
        
        return self.singlePart.as_string()
    
    def getContentType(self):
        '''
        return the Content-Type header value, including its parameters.
        '''
        return self.singlePart.get('Content-Type')
    
    def getMainPart(self):
        '''
        return the body of the message. No headers.
        '''
        return self.singlePart.get_payload()
    
def parseMIMEmessage(wholeString):   
    '''
        @param wholeString: the whole MIME message, including "Content-Type" header and
        parts 
        @return: a new HttpMessage Object with variable 'multipart' set as the
        values provided in the wholeString, or a new HttpMessageSingle Object with variable
        'singlepart' set as the values provided in the wholeString.
    '''
    msg = email.message_from_string(wholeString)
    #_structure(msg)
    if msg.get_content_type()=='multipart/related':
        return HttpMessage(msg)
    else:
        return HttpMessageSingle(msg)



    
        
def main():
    m = HttpMessage()
    m.addMainpart('Main string goes here!','text/turtle')
    m.add('XXXXABCID', 'just to try', 'text/turtle')
    print 'main part: ', m.getPart('Main')    
    print 'whole body: \n', m.getBody() 
    
    parts = m.getBody().split('\n\n', 1)
    print '[front header]: \n',parts[0]
    print '[body without header]: \n', parts[1]
    print '[body without header ends here............]'
    
    str2 = """Content-Type: multipart/related; type="text/turtle"; start="Main";
 boundary="===============7015271094629233962=="

--===============7015271094629233962==
Content-Type: text/turtle; charset="us-ascii"
Content-ID: Main

Main string goes here!
--===============7015271094629233962==
Content-Type: text/turtle; charset="us-ascii"
Content-ID: XXXXABCID

just to try
--===============7015271094629233962==--"""
    
    print '\n -----test parseMIMEmessage(): '
    parsed = parseMIMEmessage(str2)
    parsed.asString()
    print '[main part]: ', parsed.getMainPart()
    print '[Content-type]: ', parsed.getContentType()
    
    
    print '\n --------- Now testing single part ------------'
    
    m2 = HttpMessageSingle();
    m2.add('Super Mario!', 'text/turtle')
    m2.asString()
    print 'main part: ', m2.getMainPart()
    
    str3 = """Content-Type: text/turtle

    Super Mario!
    """
    print '\n ----test parseMIMEmessage(): '
    parsed2 = parseMIMEmessage(str3)
    parsed2.asString()
    print '[main part]: ', parsed2.getMainPart()
    print '[Content-type]: ', parsed2.getContentType()

if   __name__=="__main__":
    main()    
    