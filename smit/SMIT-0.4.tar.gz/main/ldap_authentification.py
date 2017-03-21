import ldap
from django.conf import settings



def set_base(base_dc):
    print "setting base"
    result = ""
    for dc in base_dc:
        result+="dc="+dc+","
    return result[:-1]

def ldapAuthentification(email, password):
    print "ldap enter"
    ZIMBRA_CONFIG = settings.SMIT_CONFIG["ldap"]
    
    base_dc = email.split('@')
    base_dc = base_dc[1].split('.')
    print set_base(base_dc)
    base =  ZIMBRA_CONFIG["ldap-base"] +","+set_base(base_dc)
    ldap_server =  ZIMBRA_CONFIG["ldap-server"]
    ldap_bind_s =  ZIMBRA_CONFIG["ldap-bind-server"]
    ldap_password_s =  ZIMBRA_CONFIG["ldap-admin-password"]
    
    """

    This function is used in the file views.py, it is used to make a LDAP authentication.
    this is returning value:
    0 : if user is not found in LDAP
    -1: if user exists but password is not matching with LDAP password
    -2: if another error occurs during this transaction.
    result: which is a dict, so ever the user is found in the LDAP server and authentication information is correct,
    "result" will contain the user email,name and department.

    """
    #ldap_config = settings.SMIT_CONFIG["ldap"]

    result = {
        'userEmail':"",
        'userName':"",
        'department':""
        }
    print "test"
    print "user = %s " % email 
    print "password = %s " % password
    
    scope = ldap.SCOPE_SUBTREE
    filter = "(mail=%s)" % email
    try:
        l = ldap.open(ldap_server)
        l.protocol_version = ldap.VERSION3
    except ldap.LDAPError:
        print "error connecting ldap"
        return -2

    try:
        #bind admin
        try:

            l.simple_bind_s(ldap_bind_s,ldap_password_s)
            print "bind ok"
        except ldap.SERVER_DOWN:
            print "bind not ok od an other think"
            return -3

        result_id = l.search(base, scope, filter, None)# None used to get all keys
        result_type, result_data = l.result(result_id, 0)
        # If the user does not exist in LDAP, Fail.

        if (len(result_data) != 1):
            return 0
        # Attempt to bind to the user's DN
        l.simple_bind_s(result_data[0][0], password)

        _dict= result_data[0][1]
        print _dict
        result['userEmail']=str(_dict['mail'])[2:-2] #removes braces and quotes
        ##result['userName']=str(_dict['displayName'])[2:-2]
        result['userName']=result['userEmail']
        
        try:
            result['department']="informatique"#str(dict[''])[2:-2]
        except KeyError:
            result['department']=None
        

        print result    
        return result

    except ldap.INVALID_CREDENTIALS:
        # Name or password were bad. Fail.
        print "failed ldap credentials"
        return -1


#print ldapAuthentification("admin@starxpert.fr","admin312")

#print "test"
#import os 
#os.chdir("/opt/smitV4/smitv4/Server")
#os.environ["DJANGO_SETTINGS_MODULE"]="settings"
