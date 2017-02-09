__author__ = 'pvde'

"""
Module to implement support for ChannelProfile in CPPA3

A ChannelProfileConfig class

"""

from lxml import etree
from copy import deepcopy
import logging, os

logging.basicConfig(level=logging.DEBUG)

_NSMAP = { 'cppa' : 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
           'pycppa3' : 'https://pypi.python.org/pypi/cppa3'}


class ChannelProfileHandler():

    def __init__(self, config=None):
        self._channel_profiles = {}
        if config != None:
            self.load_profile_config(config)

    def load_profile_config(self, parsed_config_document):
        channels = parsed_config_document.xpath('//pycppa3:ChannelProfiles/*',
                                                namespaces=_NSMAP)
        for channel in channels:
            channel_profile = channel.xpath('child::cppa:ChannelProfile/text()',
                                            namespaces = _NSMAP)[0]
            self._channel_profiles[channel_profile] = channel

    def apply_profile_configs(self, indoc):
        outdoc = etree.Element(indoc.tag, nsmap = {
            'cppa':'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0' })
        for child in indoc:
            if len(child.xpath('cppa:ChannelProfile',
                               namespaces = _NSMAP)):
                channel_profile = child.xpath('child::cppa:ChannelProfile/text()',
                                                namespaces = _NSMAP)[0]
                if channel_profile in self._channel_profiles:
                    default = self._channel_profiles[channel_profile]
                    if child.tag != default.tag:
                        raise Exception('{} != {}'.format(child.tag, default.tag))
                    logging.info('Document used a channel profile {}'.format(channel_profile))
                    child = apply_default_to_complex_subelement(child,
                                                                  default)
            outdoc.append(child)
        return outdoc

def cppa(el):
    return '{{{}}}{}'.format(_NSMAP['cppa'], el)

def pycppa3(el):
    return '{{{}}}{}'.format(_NSMAP['pycppa3'], el)


cppa3_content_model = {
    cppa('ebMS3Channel') : [cppa('Description'),
                            cppa('ChannelProfile'),
                            cppa('SOAPVersion'),
                            cppa('FaultHandling'),
                            cppa('Addressing'),
                            cppa('WSSecurityBinding'),
                            cppa('AS4ReceptionAwareness'),
                            cppa('ErrorHandling'),
                            cppa('ReceiptHandling'),
                            cppa('PullHandling'),
                            cppa('Bundling'),
                            cppa('Splitting'),
                            cppa('AlternateChannel')],

    cppa('WSSecurityBinding') : [ cppa('WSSVersion'),
                                  cppa('SecurityPolicy'),
                                  cppa('Signature'),
                                  cppa('Encryption'),
                                  cppa('UserAuthentication')],

    cppa('AS4ReceptionAwareness') : [ cppa('DuplicateHandling'),
                                      cppa('RetryHandling') ],


    cppa('DuplicateHandling') : [ cppa('DuplicateElimination'),
                                  cppa('PersistDuration') ],

    cppa('RetryHandling') : [ cppa('Retries'),
                              cppa('ExpontentialBackoff'),
                              cppa('RetryInterval')],

    cppa('Signature') : [ cppa('SignatureAlgorithm'),
                          cppa('DigestAlgorithm'),
                          cppa('CanonicalizationMethod'),
                          cppa('SignatureTransform'),
                          cppa('SigningCertificateRef'),
                          cppa('SigningCertificateRefType'),
                          cppa('SigningTrustAnchorRef'),
                          cppa('SignElements'),
                          cppa('SignAttachments'),
                          cppa('SignExternalPayloads')],

    cppa('Encryption') : [ cppa('DataEncryption'),
                           cppa('KeyEncryption'),
                           cppa('EncryptionCertificateRef'),
                           cppa('EncryptionCertificateRefType'),
                           cppa('EncryptionTrustAnchorRef')],

    cppa('DataEncryption') : [ cppa('EncryptionAlgorithm'),
                               cppa('EncryptElements'),
                               cppa('EncryptAttachments'),
                               cppa('EncryptExternalPayloads')],

    cppa('ErrorHandling') : [ cppa('DeliveryFailuresNotifyProducer'),
                              cppa('ProcessErrorNotifyConsumer'),
                              cppa('ProcessErrorNotifyProducer'),
                              cppa('SenderErrorsReportChannelId'),
                              cppa('ReceiverErrorsReportChannelId')],

    cppa('ReceiptHandling') : [ cppa('ReceiptFormat'),
                                cppa('ReceiptChannelId')]

}

def apply_default_to_complex_subelement(element, default):
    default = deepcopy(default)
    tag = element.tag
    logging.info('Apply defaults for {}'.format(tag))
    result = etree.Element(tag)
    apply_attribute_defaults(result, element)
    apply_attribute_defaults(result, default)
    if tag not in cppa3_content_model:
        logging.info('{} not in content model, taken from input'.format(tag))
        return element
    else:
        model = cppa3_content_model[tag]
        element_children = list(element)
        default_children = list(default)
        if len(element_children) == 0:
            logging.info('{} children from default'.format(tag))
            for child in default_children:
                if default_node.get(pycppa3('ifused')) == 'true':
                    logging.info('Skipped {} due to pycppa3="https://pypi.python.org/pypi/cppa3"'.format(child.tag))
                else:
                    result.append(child)
        elif len(default_children) == 0:
            logging.info('{} children from element'.format(tag))
            for child in element_children:
                result.append(child)
        else:
            # both are non-empty
            element_counter = default_counter = 0
            element_content_model_position = default_content_model_position = 0
            already_processed = []
            previous_element = None
            while element_counter < len(element_children) or default_counter < len(default_children):
                if element_counter < len(element_children) and default_counter < len(default_children):
                    element_node = element_children[element_counter]
                    default_node = default_children[default_counter]
                    #apply_attribute_defaults(element_node, default_node)
                    element_content_model_position = cppa3_content_model[tag].index(element_node.tag)
                    default_content_model_position = cppa3_content_model[tag].index(default_node.tag)
                    logging.debug('@@ {} {} {} {} {} {}'.format(element_node.tag,
                                                                element_counter,
                                                                element_content_model_position,
                                                                default_node.tag,
                                                                default_counter,
                                                                default_content_model_position))
                    if element_content_model_position == default_content_model_position:
                        logging.info('X Recursive call for {} [{},{}]'.format(element_node.tag,
                                                                            element_content_model_position,
                                                                            default_content_model_position))
                        result.append( apply_default_to_complex_subelement(element_node,
                                                                           default_node))
                        element_counter += 1
                        default_counter += 1

                    elif element_content_model_position < default_content_model_position:
                        logging.debug('Y {} [{},{}]'.format(element_node.tag,
                                                       element_content_model_position,
                                                       default_content_model_position))
                        logging.info('Content for {} taken from element [{},{}]'.format(element_node.tag,
                                                                                        element_content_model_position,
                                                                                        default_content_model_position))
                        result.append(element_node)
                        element_counter += 1

                    elif element_content_model_position > default_content_model_position:
                        logging.debug('Z {} [{},{}]'.format(element_node.tag,
                                                       element_content_model_position,
                                                       default_content_model_position))
                        if element_node.tag in already_processed:
                            logging.info('Element {} was already processed'.format(element_node.tag))
                        elif default_node.get(pycppa3('ifused')) == 'true':
                            logging.info('Skipped {} due to pycppa3="https://pypi.python.org/pypi/cppa3"'.format(default_node.tag))
                        else:
                            logging.info('Element {} to be added from default [{}]'.format(default_node.tag,
                                                                                           default_content_model_position))
                            result.append(default_node)
                        default_counter += 1

                    if previous_element != element_node.tag:
                        already_processed.append(previous_element)
                        previous_element = element_node.tag

                if element_counter == len(element_children):
                    previous_element = element_node.tag
                    already_processed.append(previous_element)


                    for child in default_children[default_counter:]:
                        logging.info('A Remaining {} children from default'.format(tag))
                        if child.get(pycppa3('ifused')) == 'true':
                            logging.info('Skipped {} due to pycppa3="https://pypi.python.org/pypi/cppa3"'.format(child.tag))
                        elif child.tag in already_processed:
                            logging.info('Skipped already processed {}'.format(child.tag))
                        else:
                            result.append(child)
                            logging.info('Supported {} due to pycppa3="https://pypi.python.org/pypi/cppa3"'.format(child.tag))
                    default_counter = len(default_children)+1


                elif default_counter == len(default_children):
                    logging.info('B Remaining {} children from element'.format(tag))
                    for child in element_children[element_counter:]:
                        result.append(child)
                    element_counter = len(element_children)+1

                previous_element = element_node.tag


        return result


def apply_attribute_defaults(provided_element, default_element):
    for att in default_element.attrib:
        if att in ['{https://pypi.python.org/pypi/cppa3}ifused']:
            pass
        elif att not in provided_element.attrib:
            provided_element.set(att, default_element.get(att))
            logging.debug('On {} setting att {} to {} {}'.format(provided_element.tag,
                                                              att,
                                                              default_element.get(att),
                                                              provided_element.tag))