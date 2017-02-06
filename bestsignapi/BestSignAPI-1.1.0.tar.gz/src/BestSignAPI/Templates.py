# This file stores data templates for each API. And we have following rules:
# 1. None value means the attribute should be added if keyword passing a value,
#    or else, do not need the attribute.
# 2. Non-empty values means we have default value on it.
# 3. Empty values means this field can be empty.
# 4. '<MUST>' means this is a must attribute, and we need a value when passing to APIs.

class Templates:
    upload_user_image = {
        'useracount': '<MUST>',
        'usermobile': '',
        'image': '<MUST>',
        'imgtype': '<MUST>',
        'imgName': '<MUST>',
        'usertype': '<MUST>',
        'username': '<MUST>',
        'updateflag': '1',
        'sealname': None,
        'sealImageType': None
    }

    query_user_image = {
        'useracount': '<MUST>',
        'sealname': None
    }

    sponsor = {
        'email':'',                     # Optional,can be empty, if it is empty,
                                        # the system will be used to provide the phone number
                                        # to generate a virtual mailbox.
        'emailtitle': '<MUST>',         # Must
        'emailcontent': '',             # Optional,can be empty
        'sxdays': '3',                  # Optional,default value 3 day
        'selfsign': '1',                # 0: No need self-sign,1:Need self-sign
        'name': '<MUST>',               # Must
        'mobile': '<MUST>',             # Must
        'usertype': '<MUST>',           # Must, 1: user,2:Enterprise
        'Signimagetype': '1',           # 0:Not generated to default Sign image.1:Generated to default Sign image
        'UserfileType': '1'             # 1: upload file from local, 2: use cloud file'
    }
    
    signatory = {
        'email': '',                    # Optional,can be empty, if it is empty,
                                        # the system will be used to provide the phone number
        'name': '<MUST>',
        'isvideo': '0',               # 1:yes, 0:no, 2:two-way,
        'mobile': '<MUST>',
        'usertype': '<MUST>',           # Must, 1: user,2:Enterprise
        'Signimagetype': '1',           # 0:Not generated to default Sign image.1:Generated to default Sign image
    }
    
    sponsor_12 = {
        'email': '',                    # Optional,can be empty, if it is empty,
                                        # the system will be used to provide the phone number
        'name': '<MUST>',
        # 'needvideo': '0',               # 1:yes, 0:no, 2:two-way,
        'mobile': '<MUST>',
        'usertype': '<MUST>',           # Must, 1: user,2:Enterprise
        'Signimagetype': '1',           # 0:Not generated to default Sign image.1:Generated to default Sign image
    }
    signatory_12  = {
        'email':'',                     # Optional,can be empty, if it is empty,
                                        # the system will be used to provide the phone number
                                        # to generate a virtual mailbox.
        'emailtitle': '<MUST>',         # Must
        'emailcontent': '111',             # Optional,can be empty
        'sxdays': '3',                  # Optional,default value 3 day
        'selfsign': '1',                # 0: No need self-sign,1:Need self-sign
        'name': '<MUST>',               # Must
        'mobile': '<MUST>',             # Must
        'usertype': '<MUST>',           # Must, 1: user,2:Enterprise
        'Signimagetype': '0',           # 0:Not generated to default Sign image.1:Generated to default Sign image
        'needvideo': '0',               # 1:yes, 0:no, 2:two-way,
        # 'UserfileType': '1'             # 1: upload file from local, 2: use cloud file'
    }

    sponsor_mayi = {
        'email':'',                     # Optional,can be empty, if it is empty,
                                        # the system will be used to provide the phone number
        'name':'<MUST>',
        # 'needvideo':'0',                # 1:yes, 0:no, 2:two-way,
        'mobile':'<MUST>',
        'usertype': '<MUST>',           # Must, 1: user,2:Enterprise
        'Signimagetype': '1',           # 0:Not generated to default Sign image.1:Generated to default Sign image
    }
    
    signatory_mayi = {
        'email':'',                     # Optional,can be empty, if it is empty,
                                        # the system will be used to provide the phone number
                                        # to generate a virtual mailbox.
        'emailtitle': '<MUST>',         # Must
        'emailcontent': '',             # Optional,can be empty
        'sxdays': '3',                  # Optional,default value 3 day
        'selfsign': '1',                # 0: No need self-sign,1:Need self-sign
        'name': '<MUST>',               # Must
        'mobile': '<MUST>',             # Must
        'usertype': '<MUST>',           # Must, 1: user,2:Enterprise
        'Signimagetype': '0',           # 0:Not generated to default Sign image.1:Generated to default Sign image
        'needvideo': '0',               # 1:yes, 0:no, 2:two-way,
    }
    
    signatory_youke = {
        'email': '',
        'name': '<MUST>',
        'needvideo': '0',
        'mobile': '<MUST>',
        'usertype': '<MUST>',
        'Signimagetype': '0',
        'identNo': '<MUST>',
        'address': '<MUST>',
        'date': '<MUST>',
        'legalperson': '<MUST>'
    }
        
    auto_sign = {
        'email': '<MUST>',              #! user account (email or cellphone number)
        'signid': '<MUST>',             # sign id
        'pagenum': '1',                 # pagenum if null, sign the last page
        'signx': '0.5',
        'signy': '0.5',
        'openflag': '1',                # 1: end, 0: no end
        'sealname': None
    }
    
    auto_sign_multi = {
        'email': '<MUST>',              #! user account (email or cellphone number)
        'signid': '<MUST>',             # sign id
        'Coordinatelist': '<MUST>',
        # 'pagenum': '1',                 # pagenum if null, sign the last page
        # 'signx': '0.5',
        # 'signy': '0.5',
        'openflag': '1',                # 1: end, 0: no end
    }
    
    sign_link_multi = {
        'mid': '<MUST>',
        'sign': '<MUST>',
        'fsid': '<MUST>',
        'email': '<MUST>',              #! user account (email or cellphone number)
        'Coordinatelist': '<MUST>',     # [{'pagenum':'1','signx':'0.5','signy':'0.1'},{'pagenum':'2','signx':'0.5','signy':'0.7'}]
        'returnurl': 'https://www.baidu.com/',
        'typedevice': '2'               # 1:pc, 2: mobile
    }

    sign_link = {
        'mid': '<MUST>',
        'sign': '<MUST>',
        'fsid': '<MUST>',
        'email': '<MUST>',              #! user account (email or cellphone number)
        'pagenum': '1',
        'signx': '0.1',
        'signy': '0.1',
        'returnurl': 'https://www.baidu.com/',
        'typedevice': '1',               # 1:pc, 2: mobile
        'openflagString': None,           # 1: end, 0: no end
        'sealname': None
    }

    apply_cfca_certificate = {
        'userType': '<MUST>',       # 1: user,2:Enterprise
        'name': '<MUST>',
        'password': '123456',       # password for use certificate
        'certificateType': '3',     # 3- General Certificate 4- Advanced Certificate
                                    # (currently does not support Advanced Certificate)
        'identType':'<MUST>',       # (personal
                                    #  0 - resident identity card
                                    #  E - booklet
                                    #  F - a temporary resident identity card)
                                    #  enterprise
                                    #  (4 - tax registration certificate
                                    #  7 - organization code certificate
                                    #  8 - business license)
        'identNo': '<MUST>',
        'duration': '24',           # Certificate validity period (month)
        'address': 'Hangzhou',
        'linkMobile': '<MUST>',
        'email': '<MUST>'
    }

    apply_zjca_certificate = {
        'userType': '<MUST>',       # 1: user,2:Enterprise
        'name': '<MUST>',
        'password': '123456',       # password for use certificate
        'linkIdCode': '<MUST>',     # Identity card number
        'icCode': '',
        'linkMan': '',
        'orgCode': '',
        'taxCode': '',
        'province': 'Zhejiang',
        'city': 'Hangzhou',
        'address': '2rd floor No. 317 Wantang RD Xihu District',
        'linkMobile': '<MUST>',
        'email': '<MUST>'
    }

    end_contract = {
        'signid': '<MUST>',
    }

    query_document = {
        'fsdid': '<MUST>'
    }
    
    create_doc_template = {
        'mid': '<MUST>',
        'sign': '<MUST>',
        'uid': '<MUST>',
        'rtick': '<MUST>',
        'typelist': '',
        'callbackurl': 'https://www.baidu.com/'
    }