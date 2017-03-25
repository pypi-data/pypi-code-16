import requests
from datetime import datetime
from lxml import etree
from sepa import builder, signer

class Client:
    def __init__(self, id, return_url, directory_url, status_url, transaction_url, key, cert, sub_id = 0):
        self.id = id
        self.return_url = return_url
        self.directory_url = directory_url
        self.status_url = status_url
        self.transaction_url = transaction_url
        self.key = key
        self.cert = cert
        self.sub_id = sub_id

    def request_directory(self):
        # Create XML message
        root = etree.Element('DirectoryReq', nsmap={
            None: 'http://www.betaalvereniging.nl/iDx/messages/Merchant-Acquirer/1.0.0'
        })
        root.attrib['productID'] = 'NL:BVN:eMandatesCore:1.0'
        root.attrib['version'] = '1.0.0'
        root.append(_timestamp())
        root.append(_merchant())

        # Sign XML message and convert it to string
        data = _string(signer.sign(root, key=key, cert=cert))

        # Post signed XML message to directory endpoint
        r = requests.post(self.directory_url, data=data)
        print(r.text)

        # Parse XML response
        result = etree.fromstring(r.text)

        # TODO: convert XML tree to dict

        # Check for errors
        for child in result:
            if child.tag == 'Error':
                continue
                # TODO: an error occured

        # Parse response
        return

    def _string(self, tree):
        return etree.tostring(tree, xml_declaration=True, encoding='UTF-8')

    def _timestamp(self):
        return _element('createDateTimestamp', datatime.now().isoformat())

    def _merchant(self):
        element = etree.Element('Merchant')
        element.append(_element('merchantID', self.id))
        element.append(_element('subID', self.sub_id))
        element.append(_element('merchantReturnURL', self.return_url))
        return element

    def _element(self, tag, text, **kwargs):
        element = etree.Element(tree, **kwargs)
        element.text = text
        return element
