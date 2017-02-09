
import unittest, lxml, logging, os

from inspect import getsourcefile
from os.path import abspath, dirname, join

from cppa3.profile import ChannelProfileHandler
from lxml import etree

class ProfileTestCase( unittest.TestCase ):

    def setUp(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="profile_test.log")
        thisdir = dirname(abspath(getsourcefile(lambda:0)))
        self.configdatadir = join(thisdir,'config')
        config_file = os.path.join(self.configdatadir,'channelprofiles.xml')
        parser = lxml.etree.XMLParser(remove_blank_text=True)
        configuration_data =  lxml.etree.parse(config_file, parser)
        self.handler = ChannelProfileHandler(configuration_data)
        self.parser = parser

    def _test_regression(self, id, created, expected):
        created_as_text = lxml.etree.tostring(created,
                                              pretty_print=True)
        expected_as_text = lxml.etree.tostring(expected,
                                              pretty_print=True)
        if created_as_text != expected_as_text:
            logging.info('Created:\n{}\nExpected:{}\n'.format(created_as_text,
                                                              expected_as_text))
            raise Exception('{}: created:\n{}\nExpected:\n{}'.format(id,
                                                                     created_as_text,
                                                                     expected_as_text))
        else:
            logging.info('Regression test for {} passed'.format(id))

    def test_0001(self):
        logging.info('Test 0001')
        data = etree.fromstring("""<?xml version="1.0"
        encoding="UTF-8"?><cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:ebMS3Channel
        xmlns:pycppa3="https://pypi.python.org/pypi/cppa3">
            <cppa:ChannelProfile>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/cprofiles/200809/as4ebhandler</cppa:ChannelProfile>
            <cppa:WSSecurityBinding>
                <cppa:Signature>
                   <cppa:SignatureAlgorithm>http://www.w3.org/2001/04/xmldsig-more#rsa-sha256</cppa:SignatureAlgorithm>
                </cppa:Signature>
            </cppa:WSSecurityBinding>
        </cppa:ebMS3Channel></cppa:CPP>
        """, self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel>
    <cppa:ChannelProfile>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/cprofiles/200809/as4ebhandler</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Signature>
        <cppa:SignatureAlgorithm>http://www.w3.org/2001/04/xmldsig-more#rsa-sha256</cppa:SignatureAlgorithm>
        <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
      </cppa:Signature>
    </cppa:WSSecurityBinding>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        self._test_regression('0001', result, expected)


    def test_0002(self):
        logging.info('Test 0002')
        data = etree.fromstring("""<?xml version="1.0"
        encoding="UTF-8"?><cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:ebMS3Channel
        xmlns:pycppa3="https://pypi.python.org/pypi/cppa3">
            <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
            <cppa:WSSecurityBinding pycppa3:ifused="true">
                <cppa:WSSVersion>1.1</cppa:WSSVersion>
            </cppa:WSSecurityBinding>
        </cppa:ebMS3Channel></cppa:CPP>
        """, self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel>
    <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Encryption>
        <cppa:DataEncryption>
          <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
          <cppa:EncryptionAlgorithm>http://www.w3.org/2001/04/xmlenc#aes128-cbc</cppa:EncryptionAlgorithm>
        </cppa:DataEncryption>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        self._test_regression('0002', result, expected)

    def test_0003(self):
        logging.info('Test 0003')
        data = etree.fromstring("""<?xml version="1.0"
        encoding="UTF-8"?><cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:ebMS3Channel
        xmlns:pycppa3="https://pypi.python.org/pypi/cppa3">
            <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
            <cppa:WSSecurityBinding pycppa3:ifused="true">
                <cppa:WSSVersion>1.1</cppa:WSSVersion>
            <cppa:Encryption>
                    <cppa:DataEncryption>
                        <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
                    </cppa:DataEncryption>
                </cppa:Encryption>
            </cppa:WSSecurityBinding>
        </cppa:ebMS3Channel></cppa:CPP>
        """, self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel>
    <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Encryption>
        <cppa:DataEncryption>
          <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
        </cppa:DataEncryption>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        self._test_regression('0003', result, expected)

    def test_0004(self):
        logging.info('Test 0004')
        data = etree.fromstring("""<?xml version="1.0"
        encoding="UTF-8"?><cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:ebMS3Channel
        xmlns:pycppa3="https://pypi.python.org/pypi/cppa3">
            <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
            <cppa:WSSecurityBinding>
                <cppa:WSSVersion>1.1</cppa:WSSVersion>
            <cppa:Encryption>
                    <cppa:DataEncryption>
                        <cppa:EncryptAttachments>true</cppa:EncryptAttachments>
                    </cppa:DataEncryption>
                </cppa:Encryption>
            </cppa:WSSecurityBinding>
        </cppa:ebMS3Channel></cppa:CPP>
        """, self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel>
    <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Encryption>
        <cppa:DataEncryption>
          <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
          <cppa:EncryptionAlgorithm>http://www.w3.org/2001/04/xmlenc#aes128-cbc</cppa:EncryptionAlgorithm>
          <cppa:EncryptAttachments>true</cppa:EncryptAttachments>
        </cppa:DataEncryption>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        self._test_regression('0004', result, expected)


    def test_0005(self):
        logging.info('Test 0005')
        data = etree.fromstring("""<?xml version="1.0"
        encoding="UTF-8"?><cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:ebMS3Channel
        xmlns:pycppa3="https://pypi.python.org/pypi/cppa3">
            <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
            <cppa:WSSecurityBinding pycppa3:ifused="true">
                <cppa:WSSVersion>1.1</cppa:WSSVersion>
            <cppa:Encryption>
                    <cppa:DataEncryption>
                        <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
                        <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes256-gcm</cppa:EncryptionAlgorithm>
                    </cppa:DataEncryption>
                </cppa:Encryption>
            </cppa:WSSecurityBinding>
        </cppa:ebMS3Channel></cppa:CPP>
        """, self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel>
    <cppa:ChannelProfile>multi_enc_alg</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Encryption>
        <cppa:DataEncryption>
          <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
          <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes256-gcm</cppa:EncryptionAlgorithm>
        </cppa:DataEncryption>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        self._test_regression('0005', result, expected)



    def test_0006(self):
        logging.info('Test 0006')
        data = etree.fromstring("""<?xml version="1.0" encoding="UTF-8"?>
        <cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
<cppa:ebMS3Channel package="entsog_package">
    <cppa:ChannelProfile>http://www.entsog.eu/publications/as4#AS4-USAGE-PROFILE/v2.0/UserMessageChannel</cppa:ChannelProfile>
    <cppa:WSSecurityBinding>
        <cppa:Signature>
            <cppa:SigningCertificateRef certId="_OYHRBO"/>
        </cppa:Signature>
        <cppa:Encryption>
            <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
        </cppa:Encryption>
    </cppa:WSSecurityBinding>
    <cppa:AS4ReceptionAwareness>
        <cppa:RetryHandling>
            <cppa:Retries>10</cppa:Retries>
        </cppa:RetryHandling>
    </cppa:AS4ReceptionAwareness>
</cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<?xml version="1.0" encoding="UTF-8"?>
        <cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
        <cppa:ebMS3Channel package="entsog_package" includeAgreementRef="false">
    <cppa:Description xml:lang="en">Channel for outgoing ENTSOG AS4 User Messages</cppa:Description>
    <cppa:ChannelProfile>http://www.entsog.eu/publications/as4#AS4-USAGE-PROFILE/v2.0/UserMessageChannel</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Signature>
        <cppa:SignatureAlgorithm>https://www.w3.org/2001/04/xmldsig-more#rsa-sha256</cppa:SignatureAlgorithm>
        <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
        <cppa:SigningCertificateRef certId="_OYHRBO"/>
      </cppa:Signature>
      <cppa:Encryption>
        <cppa:KeyEncryption>
          <cppa:EncryptionAlgorithm> http://www.w3.org/2009/xmlenc11#rsa-oaep</cppa:EncryptionAlgorithm>
          <cppa:MaskGenerationFunction>http://www.w3.org/2009/xmlenc11#mgf1sha256</cppa:MaskGenerationFunction>
          <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
        </cppa:KeyEncryption>
        <cppa:DataEncryption>
          <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
        </cppa:DataEncryption>
        <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
    <cppa:AS4ReceptionAwareness>
      <cppa:DuplicateHandling>
        <cppa:DuplicateElimination>true</cppa:DuplicateElimination>
        <cppa:PersistDuration>P10D</cppa:PersistDuration>
      </cppa:DuplicateHandling>
      <cppa:RetryHandling>
        <cppa:Retries>10</cppa:Retries>
        <cppa:RetryInterval>PT30S</cppa:RetryInterval>
      </cppa:RetryHandling>
    </cppa:AS4ReceptionAwareness>
    <cppa:ErrorHandling>
      <cppa:DeliveryFailuresNotifyProducer>true</cppa:DeliveryFailuresNotifyProducer>
      <cppa:SenderErrorsReportChannelId>incoming_sync_signal_channel</cppa:SenderErrorsReportChannelId>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
      <cppa:ReceiptChannelId>incoming_sync_signal_channel</cppa:ReceiptChannelId>
    </cppa:ReceiptHandling>
  </cppa:ebMS3Channel>
</cppa:CPP>
""", self.parser)
        self._test_regression('0006', result, expected)



    def test_0007(self):
        logging.info('Test 0007')
        data = etree.fromstring("""<?xml version="1.0" encoding="UTF-8"?>
        <cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel id="ch_receive" transport="tr_receive" package="entsog_package">
    <cppa:Description xml:lang="en">Channel for incoming ENTSOG AS4 User Messages</cppa:Description>
    <cppa:ChannelProfile>http://www.entsog.eu/publications/as4#AS4-USAGE-PROFILE/v2.0/UserMessageChannel</cppa:ChannelProfile>
    <cppa:WSSecurityBinding>
      <cppa:Encryption>
        <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
    <cppa:ErrorHandling>
      <cppa:SenderErrorsReportChannelId>ougoing_sync_signal_channel</cppa:SenderErrorsReportChannelId>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
      <cppa:ReceiptChannelId>ougoing_sync_signal_channel</cppa:ReceiptChannelId>
    </cppa:ReceiptHandling>
  </cppa:ebMS3Channel>
  <cppa:ebMS3Channel id="ch_receive" transport="tr_receive" package="entsog_package">
    <cppa:Description xml:lang="en">Channel for incoming ENTSOG AS4 User Messages</cppa:Description>
    <cppa:ChannelProfile>http://www.entsog.eu/publications/as4#AS4-USAGE-PROFILE/v2.0/UserMessageChannel</cppa:ChannelProfile>
    <cppa:WSSecurityBinding>
      <cppa:Encryption>
        <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
    <cppa:ErrorHandling>
      <cppa:SenderErrorsReportChannelId>ougoing_sync_signal_channel</cppa:SenderErrorsReportChannelId>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
      <cppa:ReceiptChannelId>ougoing_sync_signal_channel</cppa:ReceiptChannelId>
    </cppa:ReceiptHandling>
  </cppa:ebMS3Channel>
</cppa:CPP>""", self.parser)
        result = self.handler.apply_profile_configs(data)
        logging.info('Result: {}'.format(lxml.etree.tostring(result,
                                                             pretty_print=True)))
        expected = etree.fromstring("""<cppa:CPP xmlns:cppa="http://docs.oasis-open.org/ebcore/ns/cppa/v3.0">
  <cppa:ebMS3Channel id="ch_receive" transport="tr_receive" package="entsog_package" includeAgreementRef="false">
    <cppa:Description xml:lang="en">Channel for incoming ENTSOG AS4 User Messages</cppa:Description>
    <cppa:ChannelProfile>http://www.entsog.eu/publications/as4#AS4-USAGE-PROFILE/v2.0/UserMessageChannel</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Signature>
        <cppa:SignatureAlgorithm>https://www.w3.org/2001/04/xmldsig-more#rsa-sha256</cppa:SignatureAlgorithm>
        <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
      </cppa:Signature>
      <cppa:Encryption>
        <cppa:KeyEncryption>
          <cppa:EncryptionAlgorithm> http://www.w3.org/2009/xmlenc11#rsa-oaep</cppa:EncryptionAlgorithm>
          <cppa:MaskGenerationFunction>http://www.w3.org/2009/xmlenc11#mgf1sha256</cppa:MaskGenerationFunction>
          <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
        </cppa:KeyEncryption>
        <cppa:DataEncryption>
          <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
        </cppa:DataEncryption>
        <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
    <cppa:AS4ReceptionAwareness>
      <cppa:DuplicateHandling>
        <cppa:DuplicateElimination>true</cppa:DuplicateElimination>
        <cppa:PersistDuration>P10D</cppa:PersistDuration>
      </cppa:DuplicateHandling>
      <cppa:RetryHandling>
        <cppa:Retries>5</cppa:Retries>
        <cppa:RetryInterval>PT30S</cppa:RetryInterval>
      </cppa:RetryHandling>
    </cppa:AS4ReceptionAwareness>
    <cppa:ErrorHandling>
      <cppa:DeliveryFailuresNotifyProducer>true</cppa:DeliveryFailuresNotifyProducer>
      <cppa:SenderErrorsReportChannelId>ougoing_sync_signal_channel</cppa:SenderErrorsReportChannelId>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
      <cppa:ReceiptChannelId>ougoing_sync_signal_channel</cppa:ReceiptChannelId>
    </cppa:ReceiptHandling>
  </cppa:ebMS3Channel>
  <cppa:ebMS3Channel id="ch_receive" transport="tr_receive" package="entsog_package" includeAgreementRef="false">
    <cppa:Description xml:lang="en">Channel for incoming ENTSOG AS4 User Messages</cppa:Description>
    <cppa:ChannelProfile>http://www.entsog.eu/publications/as4#AS4-USAGE-PROFILE/v2.0/UserMessageChannel</cppa:ChannelProfile>
    <cppa:SOAPVersion>1.2</cppa:SOAPVersion>
    <cppa:WSSecurityBinding>
      <cppa:WSSVersion>1.1</cppa:WSSVersion>
      <cppa:Signature>
        <cppa:SignatureAlgorithm>https://www.w3.org/2001/04/xmldsig-more#rsa-sha256</cppa:SignatureAlgorithm>
        <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
      </cppa:Signature>
      <cppa:Encryption>
        <cppa:KeyEncryption>
          <cppa:EncryptionAlgorithm> http://www.w3.org/2009/xmlenc11#rsa-oaep</cppa:EncryptionAlgorithm>
          <cppa:MaskGenerationFunction>http://www.w3.org/2009/xmlenc11#mgf1sha256</cppa:MaskGenerationFunction>
          <cppa:DigestAlgorithm>http://www.w3.org/2001/04/xmlenc#sha256</cppa:DigestAlgorithm>
        </cppa:KeyEncryption>
        <cppa:DataEncryption>
          <cppa:EncryptionAlgorithm>http://www.w3.org/2009/xmlenc11#aes128-gcm</cppa:EncryptionAlgorithm>
        </cppa:DataEncryption>
        <cppa:EncryptionCertificateRef certId="_YE5XZF"/>
      </cppa:Encryption>
    </cppa:WSSecurityBinding>
    <cppa:AS4ReceptionAwareness>
      <cppa:DuplicateHandling>
        <cppa:DuplicateElimination>true</cppa:DuplicateElimination>
        <cppa:PersistDuration>P10D</cppa:PersistDuration>
      </cppa:DuplicateHandling>
      <cppa:RetryHandling>
        <cppa:Retries>5</cppa:Retries>
        <cppa:RetryInterval>PT30S</cppa:RetryInterval>
      </cppa:RetryHandling>
    </cppa:AS4ReceptionAwareness>
    <cppa:ErrorHandling>
      <cppa:DeliveryFailuresNotifyProducer>true</cppa:DeliveryFailuresNotifyProducer>
      <cppa:SenderErrorsReportChannelId>ougoing_sync_signal_channel</cppa:SenderErrorsReportChannelId>
    </cppa:ErrorHandling>
    <cppa:ReceiptHandling>
      <cppa:ReceiptChannelId>ougoing_sync_signal_channel</cppa:ReceiptChannelId>
    </cppa:ReceiptHandling>
  </cppa:ebMS3Channel>
</cppa:CPP>
""", self.parser)
        self._test_regression('0007', result, expected)

