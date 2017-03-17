'''devel try-outs


'''

import sys

import ssl
from datetime import datetime
import pytz
import OpenSSL
import socket


from ndg.httpsclient.subj_alt_name import SubjectAltName
from pyasn1.codec.der import decoder as der_decoder
import pyasn1


def get_subj_alt_name(peer_cert):
    '''
    Copied from ndg.httpsclient.ssl_peer_verification.ServerSSLCertVerification
    Extract subjectAltName DNS name settings from certificate extensions
    @param peer_cert: peer certificate in SSL connection.  subjectAltName
    settings if any will be extracted from this
    @type peer_cert: OpenSSL.crypto.X509
    '''
    # Search through extensions
    dns_name = []
    general_names = SubjectAltName()
    for i in range(peer_cert.get_extension_count()):
        ext = peer_cert.get_extension(i)
        ext_name = ext.get_short_name()
        if ext_name == "subjectAltName":
            # PyOpenSSL returns extension data in ASN.1 encoded form
            ext_dat = ext.get_data()
            decoded_dat = der_decoder.decode(ext_dat, asn1Spec=general_names)

            for name in decoded_dat:
                if isinstance(name, SubjectAltName):
                    for entry in range(len(name)):
                        component = name.getComponentByPosition(entry)
                        dns_name.append(str(component.getComponent()))
    return dns_name

def main():
    if len(sys.argv) < 2:
        print("Usage: %s hostname1 [hostname2] [hostname3] ..." % sys.argv[0])
        print('')
        print("Preparation:")
        print(" $ virtualenv venv")
        print(" $ . venv/bin/activate")
        print(" $ pip install pytz pyasn1 pyOpenSSL ndg-httpsclient")

    color = {
        False: "\033[31;1m",
        True: "\033[32;1m",
        'end': "\033[0m",
        'error': "\033[33;1m",
    }

    for server in sys.argv[1:]:
        server = server.encode('utf-8')
        ctx = OpenSSL.SSL.Context(ssl.PROTOCOL_TLSv1)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        x509 = None
        try:
            s.connect((server, 443))
            cnx = OpenSSL.SSL.Connection(ctx, s)
            cnx.set_tlsext_host_name(server)
            cnx.set_connect_state()
            cnx.do_handshake()

            x509 = cnx.get_peer_certificate()
            s.close()
        except Exception as e:
            print("%30s: %s%s%s" % (server, color['error'], e, color['end']))
            continue

        issuer = x509.get_issuer()
        issuer_corp = x509.get_issuer().organizationName
        issuer_url = x509.get_issuer().organizationalUnitName
        issuer_x509 = x509.get_issuer().commonName

        server_name = x509.get_subject().commonName
        server_name_ok = server_name == server


        from pprint import pprint
        print('##### ######')
        print(type(x509))
        pprint(dir(x509))
        #print([x509.get_extension(i).get_short_name() for i in range(x509.get_extension_count())])
        ct_precert_scts = [
            x509.get_extension(i)
            for i
            in range(x509.get_extension_count())
            if x509.get_extension(i).get_short_name() == b'ct_precert_scts'
        ][0]
        print('---')
        print(type(ct_precert_scts))
        pprint(dir(ct_precert_scts))
        pprint(dir(ct_precert_scts.get_data()))
        data_hex = ct_precert_scts.get_data()
        print(data_hex)
        print(len(data_hex))

        import binascii
        # data_der = binascii.unhexlify(data_hex)
        data_der = data_hex

        from ctutlz.sctlist import TlsExtension18
        l = TlsExtension18(data_der)

        import pdb
        pdb.set_trace()


        return  # TODO DEVEL

        try:
            subjectAltNames = get_subj_alt_name(x509)
        except pyasn1.error.PyAsn1Error:
            print('pyasn1.error.PyAsn1Error')
            subjectAltNames = []
        server_name_alt_ok = server in subjectAltNames
        if server_name_alt_ok:
            server_name_alt = server
        elif len(subjectAltNames) == 0:
            server_name_alt = None
        else:
            server_name_alt = subjectAltNames[0]

        if len(subjectAltNames) > 1:
            server_name_alt += " (+%i)" % (len(subjectAltNames) - 1)

        now = datetime.now(pytz.utc)
        begin = datetime.strptime(x509.get_notBefore().decode('ascii'), "%Y%m%d%H%M%SZ").replace(tzinfo=pytz.UTC)
        begin_ok = begin < now
        end = datetime.strptime(x509.get_notAfter().decode('ascii'), "%Y%m%d%H%M%SZ").replace(tzinfo=pytz.UTC)
        end_ok = end > now

        print("%30s: %s%30s%s (alt: %s%30s%s) begin=%s%s%s end=%s%s%s issuer=%s" % (server,
            color[server_name_ok], server_name, color['end'],
            color[server_name_alt_ok], server_name_alt, color['end'],
            color[begin_ok], begin.strftime("%d.%m.%Y"), color['end'],
            color[end_ok], end.strftime("%d.%m.%Y"), color['end'],
            issuer_corp)
        )


if __name__ == '__main__':
    main()
