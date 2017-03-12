"""
Save all attachments from an mbox file 
  options:   specify output directory
             filter by sender
             filter by recipient 
             filter by date
             specify destination diretory for attachments
             set sequence number field starting value (default 0)  
             
  usage:
   mboxattachments [--help] [--version] [--debug] [--filter_from regexp] 
                   [--filter_to regexp] [--filter_date regexp]  
                   [--exportpath path] [--SQstart value]  input_mbox_file ...
             
  attachments are stored as separate files
  file names are of the form 
  <sequence number>-<email subject>-<email sender>-<file name of attachment>
    for example, a possible file name is 
    SQ0146-CellPhone - Action-johndoe@gmail.com-myPrettyPicture.jpg
    ------ ------------------ ----------------- -------------------
    seqnum    email subject     sender           file name in email
        
    
Copyright (c) 2017    P. Andreas Moeller, Charles L. Jackson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This software is an adaption and simplification of mboxfilter
see 
  https://pypi.python.org/pypi/mboxfilter/, and
   http://pamoller.com/mboxfilter.html

"""
import email
import email.generator
import getopt
import mailbox
import os
import re
import sys
import time
import traceback # todo remove
import pdb


# Actual version:
__version__ = "0.5.35"

# Header fields containing email addresses:
HEADER_ADDRESS_FIELDS = ["From", "Cc", "Bc", "To", "Sender", "Reply-to"]

# Archive mboxes (default):
DEFAULT_ARCHIVE = True
# Cache results (default):
DEFAULT_CACHEING = False


# Email Encoding (default):
DEFAULT_ENCODING = "ISO-8859-15"
# Export attachments (default):
DEFAULT_EXPORT = True  
# Log failed mails (default):
DEFAULT_FAILURES = "fails"
# Format resu
DEFAULT_FORMAT = "%Y"
# Create result index (default):
DEFAULT_INDEX = False
# Write result sets to dir (default):
DEFAULT_OUTPUT = "."
# Maximum length of key part (default):
DEFAULT_MAXLEN = 32
# Don't display errors and statistics
DEFAULT_QUIET = False
# Separate key parts by char (default):
DEFAULT_SEPARATOR = "."
# Start SQ field in output file names 
DEFAULT_SQSTART = 0
#activate pdb debugging
DEFAULT_DEBUG = False

class FilterBaseException(Exception):
    mesg=""
    def __str__(self):
        return self.mesg

class FilterException(FilterBaseException):
    mesg = "%s"
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.mesg %self.value

class DirectoryNotExisting(FilterException):
    mesg = "direcotry not found: %s"

class HeaderMissed(FilterException):
    mesg = "header not found: %s"

class RegularExpressionError(FilterException):
    mesg = "regular expr. invalid: "

class EmailMissed(FilterBaseException):
    mesg = "email address not found"

class EmptyKeyPart(FilterBaseException):
    mesg = "key part is empty"

class CLIProtocollError(FilterBaseException):
    mesg = "syntax error, expect: Header,Regexp"

class Filter:
    # Number of deleted payloads:
    deleted = 0
    # List of indexes of payloads to be deleted:
    delete_marked = []
    # Number of exported payloads:
    exported = 0
    # Keep exported payloads
    exported_payloads = []
    # Failed while processing:
    failed = 0
    # Keep failed mails, when caching:
    failed_mails = []
    # Keep filter matches in List:
    filter_matches = []
    # Number of filtered mails:
    filtered = 0
    # Don't do indexing by default:
    indexing = False
    # Number of passed mails:
    passed = 0
    # Keep passed mails, when caching:
    passed_mails = []

    # Reference passed mails by key:
    resultset = {}

    #  Base of Sequence numbers
    SQstart = DEFAULT_SQSTART
    
        
    
        
    def __init__(self, output = DEFAULT_OUTPUT, filters = [], selectors = [],  
                 separator = DEFAULT_SEPARATOR, 
                 export_payload = DEFAULT_EXPORT, 
                 payload_exportpath = None, SQstart = DEFAULT_SQSTART, 
                 debugging = DEFAULT_DEBUG):
    
        """ Initialize a Filter object.


export_payload
    Exports payloads with a filename attribute (default True)
    

filters
    List of tuples, e.g. ("From", regexp), ("To", regexp) or ("Date", format)

output
    Saves attachements output to the given exportpath directory (default ./)


selectors
    List of tuples, e.g. ("From", None), ("To", None), ("Date", format). 
    selects mails for extracting attachments 
    
separator
    Separates key parts (default ".")


        """
        # Output files to directory:ss
        self.output = output
        if self.output is None or not os.path.isdir(self.output):
            raise DirectoryNotExisting(self.output)
        self.SQstart = SQstart
        # Filter mbox by list of filters:
        self.filters = filters
        # Sort mbox by list of selectors:
        self.selectors = selectors
        # set debugging
        self.debugging = debugging

        # TODO
        self.passed_mails = []
        # TODO
        self.passed = 0
        # Separate sort key items by:
        self.sort_key_separator = separator

        # Export payload which have a filename header field:
        self.export_payload = export_payload
                # Export payloads here:
        if payload_exportpath:
            self.payload_exportpath = payload_exportpath
        else:
            self.payload_exportpath = self.output



    def error(self, msg, mail):
        """ Output an error. """
        self.failed += 1
        if self.debugging:
            pdb.set_trace()
        pdb.set_trace()    
 
        sys.stderr.write("error: " + msg + "\n")
        try:
           self.error_pipe(mail)
        except:
           sys.stderr.write("error: can't log mail\n")

    def error_pipe(self, mail):
        """ Add mail to resultset of errors. """
        pass
    
    def output_attachment(self, path, content):
        """ Write file to path. """
        with open(path, "w+b") as fd:
            fd.write(content)

    def output_mail(self, handle, mail):
        """ Write email to filehandle. """
        genr = email.generator.Generator(handle, True, 0)
     

            
    def filter_mbox(self, obj):
        """ Filter a mbox file or mailbox.mbox instance. """
        if isinstance(obj, str):
            if os.path.isfile(obj):
                obj = mailbox.mbox(obj)
        for mail in obj:
            self.filter_mail(mail)
        if isinstance(obj, mailbox.mbox):
            obj.close()

    def filter_mail(self, mail):
        """ Filter a single mail. """
        if self.debugging:
            pdb.set_trace()
        try:
            self.filtered += 1
                        
            if self.filter_mail_pass(mail):
                if self.export_payload:
                    self.payload_parse(mail)
                self.resultset_add(mail)
                self.passed += 1

        except:
            #traceback.print_tb(sys.exc_info()[2])
            self.error(str(sys.exc_info()[1]), mail)

    def filter_mail_pass(self, mail):
        """ Apply all filters. """
        self.filter_matches = {}
        boolean = True
        for header, regexp in self.filters: 
            inner_boolean = False
            for header_value in header_values(header, mail):
                # True if any header part is true:  
                inner_boolean |= self.filter_item_pass(header, 
                                                       regexp, 
                                                       header_value)
            # True if all filter items are true:
            boolean &= inner_boolean
        return boolean
                 
    def filter_item_pass(self, header, regexp, strg):
        """ Apply filter. """
        try:
            if re.search(regexp, strg):#, flags=re.IGNORECASE):
                self.filter_matches_add(header, strg)
                return True
            return False
        except:
            raise RegularExpressionError(regexp)

    def filter_matches_add(self, key, value):
        """ Keep match of filter."""
        pass   # code left over from sqlite featuer in mboxfilter


    def payload_decode(self, payload):
        """ Decode the payload. """
        return payload.get_payload(decode=1)

    def payload_delete(self, mail):
        """ Remove makred payloads from mail. """
        offset = 0
        for idx in sorted(self.delete_marked):
            del mail.get_payload()[idx+offset]
            offset -= 1
            self.deleted += 1
        self.delete_marked = []

    def payload_export(self, payload, mail):
        """ Write payload to file. """
        fname = header_decode(payload.get_filename() or "empty")
        if fname:
            fromStr = mail["From"]
            if fromStr is None:
                fromStr = "<empty>"
            start=fromStr.find('<')+1
            end=fromStr.find('<', start)
            fromAddress=fromStr[start:end]
            if len(fromAddress) == 0:
               fromAddress="empty"
            fromAddress = fromAddress.replace("/", "") 
            #  avoid bad file names 
            
            subjectStr = mail["Subject"]
            if subjectStr is None:
               subjectStr = "empty"
            subjectStr = subjectStr[:20]  
            #  shorten to keep reasonable
            
            subjectStr = subjectStr.replace("/", "") 
            #  avoid bad file names 						

            if len(subjectStr) == 0:
               subjectStr ="empty"

            path = os.path.normpath(
                "%s/%s" % (self.payload_exportpath,
                          "-".join(["SQ%04d" %(self.exported+self.SQstart), 
                                    subjectStr, 
                                    fromAddress, 
                                    fname])
                          )
                    )


            self.output_attachment(path, self.payload_decode(payload))
            self.exported += 1
            if(self.exported == 1):
                print("initialization complete")

            print(".", end = "", flush = True)   
            #show progress but don't scroll up the screen
            
            if((self.exported % 60)  == 0):
                print(" ", flush = True)   
            #fold over every sixty files so that the dots stay visible



    def payload_handle(self, payload, mail):
        """ Handle payload by application logic and mime type. """
        if self.payload_is_handleable(payload):
            if self.export_payload:
                self.payload_pipe(payload, mail)


    def payload_index(self, payload, mail):
        """ Return index of payload """
        return mail.get_payload().index(payload)

    def payload_parse(self, mail):
        """ Handle all payloads of the mail. """
        if mail.is_multipart():
            for payload in mail.get_payload():
                if payload.get_content_maintype() == "multipart":
                    self.payload_parse(payload)
                else:
                    self.payload_handle(payload, mail)
            # Post deletion of payloads:
            self.payload_delete(mail)

    def payload_is_handleable(self, payload):
        """ Select payload for processing by mime type. """
        if payload.get_filename():
            return True
        return False

    def payload_pipe(self, payload, mail):
        """ Pipe payload either to file """
        self.payload_export(payload, mail)

    def resultset_add(self, mail):
        pass


    def resultset_pipe(self, key, mail):
        """ Pipe mail either to file or cache. """
        pass   

    def resultset_cache(self, key, mail):
        """ Cache results """
        pass


    def resultset_output(self, key, mail):
        """ Write mail to a result set. """
        handle = sys.stdout
        if key is not None:
            handle = open(os.path.normpath(self.output + "/" + key + ".mbox"),
                         "a")
        self.output_mail(handle, mail)

    
    
def header_decode(strg):
    """ Decode header field. """
    decoded = []
    for field in email.header.decode_header(strg or ""):
        decoded.append(python_decode(field[0], field[1] or DEFAULT_ENCODING))
    return "".join(decoded)

def header_email(strg):
    """ Grep email from header value """
    addr = email.utils.parseaddr(strg)
    if not addr[1]:
        raise EmailMissed(strg)
    return addr[1]
      
def header_values(header, mail):
    """ Split header into a list """
    try:
        if header not in mail.keys():
            raise HeaderMissed(header)
    except AttributeError:
        print(mail)
        return []
    values = [header_decode(mail[header])]
    if header in HEADER_ADDRESS_FIELDS:
        return [email.utils.formataddr(x) for x 
                                           in email.utils.getaddresses(values)]
    return values

def header_format(header, value, form = DEFAULT_FORMAT):
    """ Format header value by type. """
    if header in HEADER_ADDRESS_FIELDS:
        return header_email(value)
    elif header == "Date":
        parsed = email.utils.parsedate(value)
        if parsed:
            return time.strftime(form, parsed)
        return ""
    if header == "Message-ID":
        return email.utils.unquote(value)
    return value[:DEFAULT_MAXLEN]

def python_decode(strg, enc):
    """ Decode strings for python < 3. """
    if type(strg) is bytes:
        return strg.decode(enc)
    return strg

def cli_protocol(val):   
    m = re.search("^([^,;$ ]+)(?:,(.*)|()$)", val)      
    if m:
        return (m.group(1), m.group(2) or "")
    raise CLIProtocollError()

def cli_info():
    sys.stderr.write("mboxattachments v"+__version__+"\n")

def cli_usage():
    sys.stderr.write("""Usage:
    mboxattachments [--help] [--version] [--debug] [--filter_from regexp] 
                    [--filter_to regexp] [--filter_date regexp]  
                    [--exportpath path] [--SQstart value]  
                             input_mbox_file ...\n""")
 
def cli():
   cli2(sys.argv[1:])

def cli2(sys_argv1):
    """ Invoke mboxattachments from cmd."""
    #pdb.set_trace()
    # give message and exit if no arguments present
    if len(sys_argv1) == 0:
        cli_usage()
        sys.exit(1)
        
    try:
        opts, args = getopt.gnu_getopt(
            sys_argv1, 
            "abcd" , 
             [  "help", "debug", "version", "filter_from=",  
                "filter_date=", "filter_to=", 
                "exportpath=", "SQstart="])
        
        SQstart = DEFAULT_SQSTART
        output = DEFAULT_OUTPUT
        selectors = []
        archive = DEFAULT_ARCHIVE
        filters = []
        unique = False
        quiet = DEFAULT_QUIET
        failures = DEFAULT_FAILURES
        export = DEFAULT_EXPORT
        exportpath = None
        debugging = DEFAULT_DEBUG
        
        for opt, val in opts:
            val = python_decode(val, sys.stdin.encoding)
            if opt == "--dir":
             output = val
            elif opt == "--help":
                cli_usage()
                sys.exit(0)
            elif opt == "--version":
                cli_info()
                sys.exit(0)
            elif opt == "--filter_from":
                filters.append(("From", val))
            elif opt == "--filter_to":
                filters.append(("To", val))
            elif opt == "--filter_date":
                filters.append(("Date", val))
            elif opt == "--debug":
                debugging = True
                print("set debugging equal True")
            elif opt == "--exportpath":
                exportpath = val
            elif opt == "--SQstart":
                SQstart = int(val)

        print("mbox filtering beginning.  Please wait for initialization to complete.")
			
        filt = Filter(output=output,  
                      filters=filters, selectors=selectors,  
                      export_payload=export, payload_exportpath=exportpath, 
                      debugging=debugging, SQstart=SQstart)
        
        for mbox in args:
            filt.filter_mbox(mbox)
     
        print("\n\n%s emails were filtered, %s emails passed, "
            "\nprocessing of %s emails failed, "
            "\n%s attachments were exported\n" 
            %(str(filt.filtered), str(filt.passed), 
            str(filt.failed), str(filt.exported)))

    

            
            
    except getopt.GetoptError as excp:
        sys.stderr.write(str(excp)+"\n\n")
        cli_usage()
        sys.exit(1)
    except DirectoryNotExisting as excp:
        sys.stderr.write(str(excp))
        sys.exit(1)
    except SystemExit:
        pass
    except:
        traceback.print_tb(sys.exc_info()[2])
        sys.stderr.write(str(sys.exc_info()[1]));
        sys.exit(1)
        
#here begins only direct code   this allows running using the line below
#python mboxattachments --exportpath images myemails.mbox
if __name__ == "__main__":
    cli()
