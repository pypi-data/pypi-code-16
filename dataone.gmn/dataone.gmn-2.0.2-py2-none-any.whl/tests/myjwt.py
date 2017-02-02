#!/usr/bin/env python


# 3rd party
# sudo pip install cryptography pyjwt
import jwt
import cryptography.hazmat.backends
import cryptography.x509


def main():
  jwt_base64 = open('my_token.txt', 'rb').read().strip()
  # cn_pub_str = open('cn_combined.txt', 'rb').read().strip() # works
  cn_pub_str = open('cn_test_cert_1.txt', 'rb').read().strip() # works
  # cn_pub_str = open('cn_test_cert_2.txt', 'rb').read().strip() # doesn't work
  cert_obj = cryptography.x509.load_pem_x509_certificate(
    cn_pub_str,
    cryptography.hazmat.backends.default_backend(),
  )
  public_key = cert_obj.public_key()
  res = jwt.decode(jwt_base64, key=public_key, algorithms=['RS256'])
  print res


if __name__ == '__main__':
  main()
