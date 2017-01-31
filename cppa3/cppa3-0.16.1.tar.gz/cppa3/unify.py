__author__ = 'pvde'

"""
To do:

- Rename certificate IDs and IDREFs to avoid ID clashes.

- Remove Certificates that aren't referenced from the CPA.

- Improve processing of certificates and trust anchors, e.g. validation.

- Support and tests for WS-ReliableMessaging.

- ebBP attributes

- Validate Signatures on input CPPs

- Sign the generated CPA

- Split, Join, Compress

Limitations:

-  SecurityPolicy only matches "href",  does not intersect XML children.

-  Documenteer dat "id" attributen niet hoeven te matchen


"""

import lxml.etree, logging, datetime, isodate, traceback, hashlib, base64, uuid, re

from isodate.duration import Duration

from copy import deepcopy

logging.basicConfig(level=logging.DEBUG)

_NSMAP = {'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
         'ds': 'http://www.w3.org/2000/09/xmldsig#',
         'xml': 'http://www.w3.org/XML/1998/namespace',
         'xkms': 'http://www.w3.org/2002/03/xkms#',
         'dsig11' : 'http://www.w3.org/2009/xmldsig11#'
         }

def unify(acpp, bcpp, nsmap = {}, agreementidfun = None, agreementid=None,
          requested_activation_date=None, requested_expiration_date=None,
          acpp_url=None, bcpp_url=None, default_handler=None, handle_defaults=False):

    """
    @param acpp: a CPP
    @param bcpp: another CPP
    @param nsmap: optional dictionary of additional namespaces
    @param agreementidfun:  optional function to determine the agreement identifier
    @param agreementid:  optional specific agreement identifier to use
    @return:
    """
    unifier = CPABuilder(nsmap, agreementidfun, default_handler=default_handler)
    return unifier.unify(acpp, bcpp, agreementid=agreementid,
                         requested_activation_date=requested_activation_date,
                         requested_expiration_date=requested_expiration_date,
                         acpp_url=acpp_url,
                         bcpp_url=bcpp_url,
                         handle_defaults=handle_defaults)

class UnificationException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class CPABuilder():

    def __init__(self, nsmap = {}, agreementidfun = None, default_handler = None):
        """
        @param nsmap: optional dictionary of additional namespaces
        @param agreementidfun:  optional function to determine the agreement identifier
        @return:
        """
        self.reset_caches()
        self.NSMAP = {}

        self.agreementidfun = self._agreementidfun
        if agreementidfun != None:
            self.agreementidfun = agreementidfun

        self.default_handler = default_handler

        self.protocolhandlers = {
            cppa('NamedChannel'): self.unify_named_channel,
            cppa('EDIINTChannel'): self.unify_ediint_channel,
            cppa('ebMS2Channel'): self.unify_ebms2_channel,
            cppa('WSChannel'): self.unify_ws_channel,
            cppa('ebMS3Channel'): self.unify_ebms3_channel,
            cppa('TransportChannel') : self.unify_transport_channel
        }

        self.packaging_handlers = {
            cppa('SOAPWithAttachmentsEnvelope'): self.unify_soap_with_attachments_envelope,
            cppa('SimpleSOAPEnvelope'): self.unify_simple_soap_envelope,
            cppa('MIMEEnvelope'): self.unify_mime_envelope
        }

        self.mimepart_handlers = {
            cppa('CompressedSimpleMIMEPart'): self.unify_compressed_mime_part,
            cppa('MIMEMultipartRelated'): self.unify_mime_multipart_related,
            cppa('ExternalPayload'): self.unify_external_payload,
            cppa('SimpleMIMEPart'): self.unify_simple_mime_part
        }

        # load the defaults
        for prefix in _NSMAP:
            self.NSMAP[prefix] = _NSMAP[prefix]

        # load any extension namespaces
        for prefix in nsmap:
            self.NSMAP[prefix] = nsmap[prefix]

    def reset_caches(self):
        # Resets the unification data structures.
        # In the future, other data may be cached as well that is independent of the
        # input CPPs. For example, XKMS results, OCSP queries etc.
        self.included_service_specifications_counter = 0

        self.included_certificates = {}

        self.unify_channels_results = {}
        self.unify_channels_exceptions = {}

        self.unify_transport_results = {}
        self.unify_transport_exceptions = {}

        self.unify_payload_profile_results = {}
        self.unify_payload_profile_exceptions = {}

        self.unify_package_results = {}
        self.unify_package_exceptions = {}

        self.depends_on = {}

        self.included_components = {}

        self.shortened = {}
        self.collisions = {}

    def unify(self, acpp, bcpp,
              partyrole=None, counterpartyrole=None,
              agreementid = None,
              requested_activation_date=None,
              requested_expiration_date=None,
              acpp_url=None,
              bcpp_url=None,
              handle_defaults=False):
        self.reset_caches()

        logging.debug('Inline channel features ..')
        self.inline_channel_features(acpp)
        self.inline_channel_features(bcpp)

        cpp_level_acl_check(acpp, bcpp)

        if handle_defaults:
            logging.debug('Processing CPPs for defaults..')
            acpp = self.default_handler(acpp)
            bcpp = self.default_handler(bcpp)

            #logging.info('ACPP:\n{}'.format(lxml.etree.tostring(acpp,
            #                                                    pretty_print=True)))
            #logging.info('BCPP:\n{}'.format(lxml.etree.tostring(bcpp,
            #                                                    pretty_print=True)))

        cpa = lxml.etree.Element(cppa('CPA'),
                                 nsmap = self.NSMAP)
        acppid, bcppid = self.unify_profileinfo(cpa, acpp, bcpp, agreementid,
                                                requested_activation_date,
                                                requested_expiration_date,
                                                acpp_url,
                                                bcpp_url)

        self.initialize_partyinfo(cpa, acpp, 'PartyInfo')
        self.initialize_partyinfo(cpa, bcpp, 'CounterPartyInfo')
        logging.info("Unifying {} {}".format(acppid, bcppid))

        a_service_specifications = acpp.xpath('cppa:ServiceSpecification',
                                                 namespaces=self.NSMAP)

        for a_service_specification in a_service_specifications:
            logging.info('Processing service specification for {} {}'.format(
                (a_service_specification.xpath('child::cppa:PartyRole/@name',
                                              namespaces=_NSMAP))[0],
                (a_service_specification.xpath('child::cppa:CounterPartyRole/@name',
                                              namespaces=_NSMAP))[0]
            ))
            try:
                self.unify_servicebinding_list(cpa,
                                               acpp,
                                               bcpp,
                                               a_service_specification,
                                               acppid,
                                               bcppid,
                                               partyrole,
                                               counterpartyrole)
            except UnificationException as e:
                logging.info('Exception in Service Specification: {}'.format(e.value))

        if self.included_service_specifications_counter == 0:
            # There has to be at least one role pair
            # for which there is at least one matching binding
            situation = 'No matching service specifications for {}-{}'.format(acppid,
                                                                              bcppid)
            logging.info(situation)
            raise UnificationException(situation)
        else:
            logging.info('Matched {} service specification(s)'.format(self.included_service_specifications_counter))

        if 'actionbinding' in self.included_components:
            for ab in self.included_components['actionbinding']:
                if ab in self.depends_on and 'channel' in self.depends_on[ab]:
                    for dc in self.depends_on[ab]['channel']:
                        self.confirm_included('channel', dc)
                if ab in self.depends_on and 'payloadprofile' in self.depends_on[ab]:
                    for pp in self.depends_on[ab]['payloadprofile']:
                        self.confirm_included('payloadprofile', pp)

        if 'channel' in self.included_components:
            for ch in self.included_components['channel']:
                if ch in self.depends_on and 'channel' in self.depends_on[ch]:
                    for ch2 in self.depends_on[ch]['channel']:
                        self.confirm_included('channel', ch2)

            for ch in self.included_components['channel']:
                cpa.append(self.unify_channels_results[ch])

            for ch in self.included_components['channel']:
                if ch in self.depends_on and 'transport' in self.depends_on[ch]:
                    for tid in self.depends_on[ch]['transport']:
                        self.confirm_included('transport', tid)

        if 'transport' in self.included_components:
            for tp in self.included_components['transport']:
                cpa.append(self.unify_transport_results[tp])

        if 'payloadprofile' in self.included_components:
            for pp in self.included_components['payloadprofile']:
                cpa.append(self.unify_payload_profile_results[pp])

        if 'channel' in self.included_components:
            for ch in self.included_components['channel']:
                if ch in self.depends_on and 'package' in self.depends_on[ch]:
                    for ppid in self.depends_on[ch]['package']:
                        (a, b, c, d) = ppid
                        pp = self.unify_package_results[ppid]
                        logging.info("Unifying {}-{} {}-{}: {}".format(a, b, c, d, pp.tag))
                        pp.set('id', self.cppaid(a, b, c, d))
                        cpa.append(self.unify_package_results[ppid])

        return self.c14n(cpa)

    def c14n(self, tree):
        newtree = lxml.etree.Element(tree.tag, nsmap=self.NSMAP)
        newtree.text = tree.text
        for att in tree.attrib:
            newtree.attrib[att] = tree.attrib[att]
        for element in tree:
            if element is None:
                pass
            #elif lxml.etree.iselement(element):
            elif type(element) is lxml.etree._Element:
                newtree.append(self.c14n(element))
            else:
                newtree.append(element)
        return newtree

    def unify_profileinfo(self, cpa, acpp, bcpp, agreementid=None,
                          requested_activation_date=None,
                          requested_expiration_date=None,
                          acpp_url=None,
                          bccp_url=None):
        acppid = acpp.xpath('child::cppa:ProfileInfo/cppa:ProfileIdentifier/text()',
                            namespaces=self.NSMAP)[0]
        bcppid = bcpp.xpath('child::cppa:ProfileInfo/cppa:ProfileIdentifier/text()',
                            namespaces=self.NSMAP)[0]
        agreementinfo = lxml.etree.SubElement(cpa,
                                              cppa('AgreementInfo'))
        agreementidel = lxml.etree.SubElement(agreementinfo,
                                            cppa('AgreementIdentifier'))
        #agreementid.text = "{}_{}".format(acppid, bcppid)
        if agreementid != None:
            agreementidel.text = agreementid
        else:
            agreementidel.text = self.agreementidfun(acpp, bcpp)
        agreementdescription = lxml.etree.SubElement(agreementinfo, cppa('Description'))
        agreementdescription.text = "Agreement formed from {} and {} at {}".format(acppid,
                                                                                   bcppid,
                                                                                   datetime.datetime.now().isoformat())
        agreementdescription.set(xml('lang'), 'en')
        for (pid, pid_url) in [(acppid, acpp_url),
                               (bcppid, bccp_url)]:
            pid2 = lxml.etree.SubElement(agreementinfo, cppa('ProfileIdentifier'))
            pid2.text = pid
            if pid_url != None:
                pid2.set('href', pid_url)

        self.init_activation_date(acpp, bcpp, agreementinfo,
                                  requested_activation_date,
                                  requested_expiration_date)
        return acppid, bcppid

    def init_activation_date(self, acpp, bcpp, agreementinfo,
                             requested_activation_date=None,
                             requested_expiration_date=None):
        now = datetime.datetime.now()
        try:
            aphasein = acpp.xpath('child::cppa:ProfileInfo/cppa:PhaseIn/text()',
                                  namespaces=self.NSMAP)[0]
            aduration = isodate.isoduration.parse_duration(aphasein)
        except:
            aduration = datetime.timedelta(0)
        try:
            bphasein = bcpp.xpath('child::cppa:ProfileInfo/cppa:PhaseIn/text()',
                                  namespaces=self.NSMAP)[0]
            bduration = isodate.isoduration.parse_duration(bphasein)
        except:
            bduration = datetime.timedelta(0)

        if aduration < bduration:
            earliest = now + bduration
        else:
            earliest = now + aduration

        if requested_activation_date != None:
            if requested_activation_date > earliest:
                earliest = requested_activation_date

        for cpp in [acpp, bcpp]:
            activationl = cpp.xpath('child::cppa:ProfileInfo/cppa:ActivationDate/text()',
                                    namespaces=self.NSMAP)
            if len(activationl) > 0:
                activation = isodate.isodatetime.parse_datetime(activationl[0])
                if activation > earliest:
                    earliest = activation

        activationdate = lxml.etree.SubElement(agreementinfo, cppa('ActivationDate'))
        activationdate.text = earliest.isoformat()

        expirationdefault = None
        for cpp in [acpp, bcpp]:
            expirationL = cpp.xpath('child::cppa:ProfileInfo/cppa:ExpirationDate/text()',
                                    namespaces=self.NSMAP)
            if len(expirationL) > 0:
                expiration = isodate.isodatetime.parse_datetime(expirationL[0])

                if requested_expiration_date != None:
                    if requested_expiration_date < expiration:
                        expiration = requested_expiration_date

                if expiration < earliest:
                    situation = 'Service expires at {} before earliest activation {}'.format(expirationL[0],
                                                                                             earliest.isoformat())
                    logging.info(situation)
                    raise UnificationException(situation)
                if expirationdefault is None:
                    expirationdefault = expiration
                elif expiration < expirationdefault:
                    expirationdefault = expiration

        if not expirationdefault is None:
            expirationdate = lxml.etree.SubElement(agreementinfo, cppa('ExpirationDate'))
            expirationdate.text = expirationdefault.isoformat()

    def _agreementidfun(self, acpp, bcpp):
        acppid = acpp.xpath('child::cppa:ProfileInfo/cppa:ProfileIdentifier/text()',
                            namespaces=self.NSMAP)[0]
        bcppid = bcpp.xpath('child::cppa:ProfileInfo/cppa:ProfileIdentifier/text()',
                            namespaces=self.NSMAP)[0]
        return "{}_{}".format(acppid, bcppid)

    def initialize_partyinfo(self, cpa, cpp, element):
        partyinfo = lxml.etree.SubElement(cpa, cppa(element))

        inelement = cpp.xpath('child::cppa:PartyInfo',
                              namespaces=self.NSMAP)[0]
        for pname in inelement.xpath('child::cppa:PartyName',
                               namespaces= self.NSMAP):
            partyinfo.append( deepcopy(pname))
        for pid in inelement.xpath('descendant-or-self::cppa:PartyId',
                             namespaces= self.NSMAP):
            partyinfo.append( deepcopy(pid))
        for certificate in inelement.xpath('child::cppa:Certificate',
                                           namespaces= self.NSMAP):
            partyinfo.append(deepcopy(certificate))
        for certificate in inelement.xpath('child::cppa:IDPRegistration',
                                           namespaces= self.NSMAP):
            partyinfo.append(deepcopy(certificate))
        for certificate in inelement.xpath('child::cppa:IDPRegistrationSet',
                                           namespaces= self.NSMAP):
            partyinfo.append(deepcopy(certificate))


        return partyinfo

    def unify_servicebinding_list(self,
                                  cpa, acpp, bcpp,
                                  a_service_specification,
                                  acppid, bcppid,
                                  partyrole, counterpartyrole,
                                  bindings_match_mode='all'):
        arole = a_service_specification.xpath('child::cppa:PartyRole/@name',
                                      namespaces=self.NSMAP)[0]
        brole = a_service_specification.xpath('child::cppa:CounterPartyRole/@name',
                                      namespaces=self.NSMAP)[0]

        if (partyrole is None or partyrole == arole) \
                and (counterpartyrole is None or counterpartyrole == brole):

            service_specification = lxml.etree.Element(cppa('ServiceSpecification'))

            lxml.etree.SubElement(service_specification, cppa('PartyRole'), name=arole)
            lxml.etree.SubElement(service_specification, cppa('CounterPartyRole'), name=brole)

            xpqt = 'cppa:ServiceSpecification[cppa:PartyRole/@name = "{}"' \
                   'and cppa:CounterPartyRole/@name = "{}"]'

            xpq = xpqt.format(brole, arole)
            try:
                b_service_specification = bcpp.xpath(xpq,
                                                   namespaces=self.NSMAP)[0]
            except IndexError:
                situation = 'No ServiceSpecification for {} {} in {}'.format(brole,
                                                                             arole,
                                                                             bcppid)
                logging.info(situation)
                if partyrole is not None and counterpartyrole is not None:
                    """
                    We raise an exception if unification was requested for a specific
                    PartyRole-CounterPartyRole combination.
                    Otherwise, we assume it can just be ignored.
                    """
                    raise UnificationException(situation)

            else:
                logging.info('Processing ACL checks for service {} {}'.format(arole,
                                                                              brole))
                service_specification_acl_check(a_service_specification,
                                                acpp,
                                                b_service_specification,
                                                bcpp)
                logging.info('Processing service bindings for {} {}'.format(arole, brole))
                a_servicebinding_list = a_service_specification.xpath('child::cppa:ServiceBinding',
                                                                      namespaces=self.NSMAP)
                included_bindings_counter = 0
                last_exception = None
                for counter, a_servicebinding in enumerate(a_servicebinding_list, start=1):
                    try:
                        logging.info('Service binding #{}'.format(counter))
                        acpa_servicebinding = self.unify_servicebinding_from_acpp_party(acppid,
                                                                                       acpp,
                                                                                       bcppid,
                                                                                       bcpp,
                                                                                       arole,
                                                                                       brole,
                                                                                       a_servicebinding,
                                                                                       b_service_specification)
                    except UnificationException as e:
                        last_exception = e
                        if bindings_match_mode == 'all':
                            logging.info("UnificationException: {}".format(e.value))
                            logging.info('Bindings match mode {} '\
                                    'so abandoning service specification'.format(bindings_match_mode))
                            # @@@ review the following
                            # #raise
                        else:
                            logging.info('Bindings match mode {}'\
                                    'so ignoring {}'.format(bindings_match_mode,
                                                            e.value))
                    else:
                        included_bindings_counter += 1
                        service_specification.append(acpa_servicebinding)
                        logging.info('Computed {} service binding(s)'.format(included_bindings_counter))

                if included_bindings_counter > 0:
                    logging.info('Total service bindings is {}'.format(included_bindings_counter))
                    cpa.append(service_specification)
                    self.included_service_specifications_counter += 1
                    #logging.info(lxml.etree.tostring(cpa, pretty_print=True) )
                else:
                    situation = 'No Service Bindings matched for {}-{} {}-{}: {}'.format(acppid,
                                                                                         arole,
                                                                                         bcppid,
                                                                                         brole,
                                                                                         last_exception)
                    logging.info(situation)
                    raise UnificationException(situation)
        else:
            logging.info("Skipping role {}".format(arole))

    def unify_servicebinding_from_acpp_party(self,
                                            acppid,
                                            acpp,
                                            bcppid,
                                            bcpp,
                                            arole,
                                            brole,
                                            a_servicebinding,
                                            b_service_specification):
        acpa_servicebinding = lxml.etree.Element(cppa('ServiceBinding'))

        aserviceEl = a_servicebinding.xpath('child::cppa:Service',
                                           namespaces=self.NSMAP)[0]
        aservice = aserviceEl.text
        aservicetype = aserviceEl.get('type')
        logging.info("Processing service {} type {}".format(aservice, aservicetype))
        acpaservice = lxml.etree.SubElement(acpa_servicebinding, cppa('Service'))
        acpaservice.text = aservice
        if aservicetype is not None:
            acpaservice.set('type', aservicetype)
        if aservicetype is None:
            bserviceq = 'child::cppa:ServiceBinding[cppa:Service="{}"]'.format(aservice)
        else:
            bserviceqt = 'child::cppa:ServiceBinding[cppa:Service[text()="{}" and @type="{}"]]'
            bserviceq = bserviceqt.format(aservice, aservicetype)
        try:
            b_servicebinding = b_service_specification.xpath(bserviceq,
                                                          namespaces=self.NSMAP)[0]
        except:
            raise UnificationException('Service {} not found for {} {} in {}'.format(aservice,
                                                                                     brole,
                                                                                     arole,
                                                                                     bcppid))
        else:
            logging.info("Unifying definitions for service {}, type {} in role {}".format(aservice, aservicetype, arole))
            self.unify_servicebinding(acppid, acpp,
                                      bcppid, bcpp,
                                      aservice,
                                      a_servicebinding, b_servicebinding,
                                      acpa_servicebinding)
        return acpa_servicebinding

    def unify_servicebinding(self, acppid, acpp, bcppid, bcpp, service,
                             a_servicebinding, b_servicebinding,
                             servicebinding):
        logging.info("Unifying service {} in {} and {}".format(service, acppid, bcppid))


        service_binding_acl_check(a_servicebinding, acpp,
                                  b_servicebinding, bcpp)

        (identifiers, actions) = self.unify_send_receive(acppid, acpp, bcppid, bcpp, service,
                                                         a_servicebinding, b_servicebinding,
                                                         servicebinding,
                                                         "send", "receive",
                                                         action_identifiers =[],
                                                         actions=[])
        (identifiers2, actions2) = self.unify_send_receive(acppid, acpp, bcppid, bcpp, service,
                                                           a_servicebinding, b_servicebinding,
                                                           servicebinding,
                                                           "receive", "send",
                                                           action_identifiers=identifiers,
                                                           actions=actions)
        logging.info("Unified service binding in {} and {} for {}".format(acppid, bcppid, service))
        logging.debug("Identifier list for {}, {}, {}: {}".format(acppid,
                                                                  bcppid,
                                                                  service,
                                                                  identifiers2))
        self.check_b_servicebinding(actions2, b_servicebinding)

        for id in identifiers2:
            self.confirm_included('actionbinding', id)
            #if id in self.depends_on and 'channel' in self.depends_on[id]:
            #    for id2 in self.depends_on[id]['channel']:
            #        self.confirm_included('channel', id2)

    def unify_send_receive(self,
                           acppid, acpp,
                           bcppid, bcpp,
                           service,
                           a_servicebinding, b_servicebinding,
                           ab_servicebinding,
                           atype, btype,
                           action_identifiers = [],
                           actions = []):

        try:
            asendbinding_list = a_servicebinding.xpath('child::cppa:ActionBinding[@sendOrReceive="{}"]'.format(atype),
                                                       namespaces=self.NSMAP)

            for a_binding in asendbinding_list:
                action = a_binding.get('action')
                aid = a_binding.get('id')
                logging.info('Processing Service {}, Action {}'.format(service, action))

                actionbinding = lxml.etree.Element(cppa('ActionBinding'),
                                                   id=aid, sendOrReceive=atype, action=action)
                a_reply_to = a_binding.get('replyTo')
                if a_reply_to is not None:
                    actionbinding.set('replyTo', a_reply_to)

                bexpr = 'child::cppa:ActionBinding[@action="{}" and @sendOrReceive="{}"]'.format(action,
                                                                                                 btype)

                b_binding_list = b_servicebinding.xpath(bexpr,
                                                        namespaces=self.NSMAP)
                if len(b_binding_list) == 1:
                    b_binding = b_servicebinding.xpath(bexpr,
                                                       namespaces=self.NSMAP)[0]
                    bid = b_binding.get('id')
                    logging.info("Unifying {}-{} in {} and {} channels {} - {}".format(service,
                                                                                       action,
                                                                                       acppid,
                                                                                       bcppid,
                                                                                       aid,
                                                                                       bid))

                    try:
                        logging.info('Checking action binding level ACL')
                        action_binding_acl_check(a_binding, acpp,
                                                 b_binding, bcpp)
                    except UnificationException as e:
                        use = a_binding.get('use')
                        if use == 'optional' or use == None:
                            logging.info('ACL ignored for optional action binding {}'.format(e.value))
                        else:
                            logging.info('Exception for action binding {}'.format(e.value))
                    else:
                        self.check_action_replyto(service, action, a_reply_to, b_binding,
                                                  a_servicebinding, b_servicebinding)

                        # PayloadProfile
                        appid = a_binding.get('payloadProfileId')
                        bppid = b_binding.get('payloadProfileId')
                        if appid is not None and bppid is not None:
                            self.unify_payload_profile(acppid, acpp, bcppid, bcpp, appid, bppid)
                            logging.info('Setting attribute to {} for {} {} {} {}'.format(self.cppaid(acppid, appid, bcpp, bppid),
                                                                                          acppid,
                                                                                          appid,
                                                                                          bcppid, bppid))
                            actionbinding.set('payloadProfileId', self.cppaid(acppid, appid, bcppid, bppid))
                            self.record_dependency((acppid, aid, bcppid, bid),
                                                   'payloadprofile',
                                                   (acppid, appid, bcppid, bppid))

                        (acppid, acid, bcppid, bcid) = self.unify_actionbinding(acppid, acpp,
                                                                                bcppid, bcpp,
                                                                                service, action,
                                                                                aid, a_binding,
                                                                                bid, b_binding,
                                                                                atype)
                        logging.info("Successfully unified {}-{}  ({} {}) to {}: {} {} {}".format(service, action,
                                                                                                  acppid, aid,
                                                                                                  bcppid, bid,
                                                                                                  acid, bcid))

                        action_identifiers.append((acppid, aid, bcppid, bid))
                        actions.append(action)

                        self.record_dependency((acppid, aid, bcppid, bid),
                                               'channel',
                                               (acppid, acid, bcppid, bcid))

                        acpachannelid = lxml.etree.SubElement(actionbinding, cppa('ChannelId'))
                        acpachannelid.text = self.cppaid(acppid, acid, bcppid, bcid)

                        # Properties
                        self.unify_properties(aid, acpp, a_binding,
                                              bid, bcpp, b_binding, actionbinding)

                        ab_servicebinding.append(actionbinding)

                else:
                    use = a_binding.get('use')
                    logging.info("No match in {} for {}-{} ({})".format(bcppid, service, action,
                                                                        use))
                    if use != 'optional':
                        raise UnificationException("No match in {} for {}-{}".format(bcppid, service, action))

        except UnificationException as e:
            logging.info("Send_Receive exception: {}".format(e.value))
            raise
        else:
            return action_identifiers, actions

    def check_action_replyto(self, service, action, areplyTo,
                             b_binding, a_servicebinding, b_servicebinding):
        b_reply_to = b_binding.get('replyTo')

        if areplyTo is None and b_reply_to is not None \
            or areplyTo is not None and b_reply_to is None:
            raise UnificationException('Bindings {} {} inconsistent for replyTo presence'.format(service,
                                                                                                 action))
        if areplyTo is not None and b_reply_to is not None:
            arsendbinding = a_servicebinding.xpath('child::cppa:ActionBinding[@id="{}"]'.format(areplyTo),
                                                  namespaces=self.NSMAP)[0]
            brsendbinding = b_servicebinding.xpath('child::cppa:ActionBinding[@id="{}"]'.format(b_reply_to),
                                                  namespaces=self.NSMAP)[0]
            araction = arsendbinding.get('action')
            braction = brsendbinding.get('action')

            if araction != braction:
                raise UnificationException('Bindings {} replyTo to different actions {} {}'.format(service,
                                                                                                   araction,
                                                                                                   braction))

    def check_b_servicebinding(self, covered_actions, b_servicebinding):
        b_abinding_list = b_servicebinding.xpath('child::cppa:ActionBinding',
                                                 namespaces=self.NSMAP)
        for b_abinding in b_abinding_list:
            action = b_abinding.get('action')
            if action in covered_actions:
                logging.debug('{} found in covered action list'.format(action))
            else:
                use = b_abinding.get('use')
                if use == 'optional':
                    logging.debug('{} not found in covered action list, but it is optional'.format(action))
                else:
                    raise UnificationException('Required binding for action {} not matched'.format(action))

    def unify_actionbinding(self, acppid, acpp, bcppid, bcpp, service, action,
                            aid, a_binding, bid, b_binding, direction):
        logging.info("Merging action bindings {} and {} for {} -- {}".format(aid, bid, service, action))

        # Channels
        achannelids = a_binding.xpath('child::cppa:ChannelId/text()', namespaces=self.NSMAP)
        bchannelids = b_binding.xpath('child::cppa:ChannelId/text()', namespaces=self.NSMAP)

        last_exception = None

        for (acounter, acid) in enumerate(achannelids):
            for (bcounter, bcid) in enumerate(bchannelids):
                logging.info("Attempt to unify {} #{} and {} #{}".format(acid,
                                                                         acounter,
                                                                         bcid,
                                                                         bcounter))
                abchannelid = (acppid, acid, bcppid, bcid)
                try:
                    logging.info("Attempting to unify channel {} for {}".format(bcounter,
                                                                                abchannelid))
                    self.unify_channels(abchannelid, acpp, bcpp, direction)
                except UnificationException as e:
                    last_exception = e
                    logging.info("Failure to unify {} #{} and {} #{}: {}".format(acid,
                                                                                 acounter,
                                                                                 bcid,
                                                                                 bcounter,
                                                                                 e.value))

                else:
                    logging.info("Successfully unified {} #{} and {} #{}".format(acid,
                                                                                 acounter,
                                                                                 bcid,
                                                                                 bcounter))

                    #self.confirm_included('actionbinding', (acppid, aid, bcppid, bid))
                    return abchannelid
        raise UnificationException('Action bindings {} {} failed to unify: {}'.format(aid,
                                                                                      bid,
                                                                                      last_exception.value))

    def unify_channels(self, abchannelid, acpp, bcpp, direction):
        (acppid, acid, bcppid, bcid) = abchannelid

        cached, result = self.memo(acppid,
                                   acid,
                                   bcppid,
                                   bcid,
                                   self.unify_channels_results,
                                   self.unify_channels_exceptions)
        if cached:
            logging.info("Found cached channel for {} {} and {} {}".format(acppid, acid, bcppid, bcid))
            return result
        try:
            result = self.unify_channels_memo(acpp, bcpp, abchannelid, acid, bcid, direction)
        except UnificationException as e:
            logging.info("Exception unifying channel for {} {} and {} {}: {}".format(acppid, acid,
                                                                                     bcppid, bcid,
                                                                                     e.value))
            self.unify_channels_exceptions[acppid,
                                           acid,
                                           bcppid,
                                           bcid] = e
            raise
        else:
            self.unify_channels_results[acppid,
                                        acid,
                                        bcppid,
                                        bcid] = result
            logging.info("Unified channel for {} {} and {} {}".format(acppid, acid, bcppid, bcid))
            return result

    def unify_channels_memo(self, acpp, bcpp, abchannelid, a_channelid, b_channelid, direction):
        (acppid, acid, bcppid, bcid) = abchannelid
        logging.info("Unifying channel {} {} {} and {} {} {}".format(acppid,
                                                                     acid,
                                                                     a_channelid,
                                                                     bcppid,
                                                                     bcid,
                                                                     b_channelid))
        abxid = (acppid, a_channelid, bcppid, b_channelid)
        try:
            if a_channelid is b_channelid is None:
                return abxid
            elif a_channelid is None or b_channelid is None:
                raise UnificationException('Missing channel {} versus {}'.format(a_channelid,
                                                                                 b_channelid))
            else:
                a_channel = acpp.xpath('descendant::node()[@id="{}"]'.format(a_channelid),
                                 namespaces=self.NSMAP)[0]
                b_channel = bcpp.xpath('descendant::node()[@id="{}"]'.format(b_channelid),
                                 namespaces=self.NSMAP)[0]
                if a_channel.tag != b_channel.tag:
                    raise UnificationException('Incompatible channel types {} {}'.format(a_channel.tag,
                                                                                         b_channel.tag))
                elif a_channel.tag not in self.protocolhandlers:
                    raise UnificationException('Unsupported channel type {} {}'.format(a_channel.tag,
                                                                                       b_channel.tag))
                else:
                    try:
                        handler = self.protocolhandlers[a_channel.tag]
                        ab_channel = lxml.etree.Element(a_channel.tag)
                        abdxid = self.cppaid(acppid, a_channelid, bcppid, b_channelid)
                        ab_channel.set('id', abdxid)
                        return handler(acpp,
                                       bcpp,
                                       abxid,
                                       a_channel,
                                       b_channel,
                                       ab_channel,
                                       direction)
                    except UnificationException as e:
                        raise UnificationException('Mismatch in channel for protocol {}: {}'.format(a_channel.tag,
                                                                                                    e.value))
        except UnificationException as e:
            te = 'Channel unification exception for {}: {}'.format(abchannelid, e.value)
            raise UnificationException(te)

    """
    Channel Bindings
    """
    def unify_channel_descriptions(self, abxid, a_channel, b_channel, binding):
        (acppid, axid, bcppid, bxid) = abxid
        description = lxml.etree.SubElement(binding, cppa('Description'))
        description.text = 'Channel formed from {} ({}) in {} and {} ({}) in {}'.format(a_channel.get('id'),
                                                                                        get_description_value_if_present(a_channel),
                                                                                        acppid,
                                                                                        b_channel.get('id'),
                                                                                        get_description_value_if_present(b_channel),
                                                                                        bcppid)
        description.set(xml('lang'), 'en')

    def unify_channel_max_size(self, a_channel, b_channel, ab_channel):
        try:
            a_max_size = int(a_channel.xpath('child::cppa:MaxSize/text()',
                                         namespaces=self.NSMAP)[0])
        except:
            a_max_size = 0

        try:
            b_max_size = int(b_channel.xpath('child::cppa:MaxSize/text()',
                                         namespaces=self.NSMAP)[0])
        except:
            b_max_size = 0
        if a_max_size == b_max_size == 0:
            pass
        else:
            if a_max_size > b_max_size:
                ab_max_size = b_max_size
            else:
                ab_max_size = a_max_size
            ab_max_size_el = lxml.etree.SubElement(ab_channel,cppa('MaxSize'))
            ab_max_size_el.text = str(ab_max_size)
            logging.info("Unifying Maxsize, {} {} {}".format(a_max_size, b_max_size, ab_max_size))


    """
    Named Channel
    """
    def unify_named_channel(self,
                            acpp,
                            bcpp,
                            ab_channelid,
                            a_channel,
                            b_channel,
                            binding,
                            direction):
        (acppid, axid, bcppid, bxid) = ab_channelid

        self.unify_channel_descriptions(ab_channelid, a_channel, b_channel, binding)
        self.unify_channel_max_size(a_channel, b_channel, binding)
        self.unify_simple_subelement(a_channel, b_channel, binding,
                                     'cppa', 'ChannelName')


        self.unify_simple_subelement(a_channel, b_channel, binding,
                                     'cppa', 'SigningCertificateRef',
                                     strictelements=False, required=False)
        self.unify_simple_subelement(a_channel, b_channel, binding,
                                     'cppa', 'EncryptionCertificateRef',
                                     strictelements=False, required=False)

        self.unify_signing_cert_and_anchor(acppid, acpp, bcppid, bcpp,
                                           a_channel, b_channel, direction)
        self.unify_encryption_cert_and_anchor(acppid, acpp, bcppid, bcpp,
                                              a_channel, b_channel, direction)

        a_transport_id = a_channel.get('transport')
        b_transport_id = b_channel.get('transport')
        self.unify_transport(acppid, acpp,
                             bcppid, bcpp,
                             a_transport_id, b_transport_id,
                             direction)

        self.record_dependency(ab_channelid, 'transport', (acppid, a_transport_id,
                                                           bcppid, b_transport_id))
        ab_transport_id = self.cppaid(acppid,
                                      a_transport_id,
                                      bcppid,
                                      b_transport_id)
        binding.set('transport', ab_transport_id)

        # to do:   match Params
        return binding

    """
    EDIINT
    """
    def unify_ediint_channel(self, acpp, bcpp, abxid,
                             a_channel, b_channel, binding, direction):
        (acppid, axid, bcppid, bxid) = abxid
        self.unify_channel_descriptions(abxid, a_channel, b_channel, binding)
        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, binding,
                                      'cppa', 'Signature',
                                      self.unify_signature, direction)
        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, binding,
                                      'cppa', 'Encryption',
                                      self.unify_encryption, direction)

        atid = a_channel.get('transport')
        btid = b_channel.get('transport')
        self.unify_transport(acppid, acpp,
                             bcppid, bcpp,
                             atid, btid,
                             direction)

        self.record_dependency(abxid, 'transport', (acppid, atid, bcppid, btid))
        abtid = self.cppaid(acppid, atid, bcppid, btid)
        binding.set('transport', abtid)
        return binding

    """
    ebMS2
    """
    def unify_ebms2_channel(self, acpp, bcpp, abxid,
                            a_channel, b_channel, binding, direction):
        (acppid, acid, bcppid, bcid) = abxid
        logging.info("Unifying ebMS2Channel for {} {}".format(acid, bcid))
        self.unify_as_response(acid, a_channel, bcid, b_channel, binding)
        self.unify_channel_descriptions(abxid, a_channel, b_channel, binding)
        self.unify_transport_elements(acppid, acpp, bcppid, bcpp, a_channel, b_channel,
                                      abxid, binding, direction)

        self.unify_package_elements(acppid, acpp, bcppid, bcpp, a_channel, b_channel,
                                    abxid, binding, direction)
        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, binding,
                                      'cppa', 'ErrorHandling',
                                      self.unify_error_handling, direction)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, binding,
                                      'cppa', 'ReceiptHandling',
                                      self.unify_receipt_handling, direction)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, binding,
                                      'cppa', 'ebMS2ReliableMessaging',
                                      self.unify_ebms2_reliable_messaging, direction)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, binding,
                                      'cppa', 'ebMS2SecurityBinding',
                                      self.unify_ebms2_security_binding, direction)

        return binding

    def unify_ebms2_reliable_messaging(self, acpp, bcpp, abxid,
                                       ael, bel, abel, direction):
        unify_atts(ael, bel, abel, strictatts=True)
        self.unify_complex_subelement(acpp, bcpp, abxid, ael, bel, abel,
                                      'cppa', 'DuplicateHandling',
                                      self.unify_duplicate_handling)
        self.unify_persist_duration(acpp, bcpp, abxid, ael, bel, abel, direction)
        self.unify_retry_handling(acpp, bcpp, abxid, ael, bel, abel, direction)


    def unify_ebms2_security_binding(self, acpp, bcpp, abxid,
                                     asec, bsec, security, direction):
        self.unify_complex_subelement(acpp, bcpp, abxid, asec, bsec, security,
                                      'cppa', 'Signature',
                                      self.unify_signature, direction)
        self.unify_complex_subelement(acpp, bcpp, abxid, asec, bsec, security,
                                      'cppa', 'Encryption',
                                      self.unify_encryption, direction)

    """
    Web Services
    """
    def unify_ws_channel(self, acpp, bcpp, abxid,
                         a_channel, b_channel, binding, direction):
        (acppid, axid, bcppid, bxid) = abxid
        self.unify_channel_descriptions(abxid, a_channel, b_channel, binding)
        self.unify_simple_subelement(a_channel, b_channel, binding, 'cppa', 'SOAPVersion',
                                     required=False)
        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, binding,
                                      'cppa', 'WSSecurityBinding',
                                      self.unify_ws_security, direction)
        return binding

    """
    Transport Channels
    """
    def unify_transport_channel(self, acpp, bcpp, abxid,
                                a_channel, b_channel, binding, direction):
        (acppid, acid, bcppid, bcid) = abxid
        self.unify_transport_elements(acppid, acpp, bcppid, bcpp, a_channel, b_channel,
                                      abxid, binding, direction)
        self.unify_channel_descriptions(abxid, a_channel, b_channel, binding)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, binding,
                                      'cppa', 'RequestChannelID',
                                      self.unify_request_channel_id, direction)
        return binding

    def unify_request_channel_id(self, acpp, bcpp, abxid,
                                 arerc, brerc, abrerc, direction):
        (acppid, axid, bcppid, bxid) = abxid
        logging.info('unify_RequestChannelId for {} {}'.format(abxid, arerc))
        arercid = arerc.text
        brercid = brerc.text
        self.unify_channels((acppid, arercid, bcppid, brercid), acpp, bcpp, None)
        logging.info("Unified RequestChannelId {} {}".format(arercid, brercid))
        abrerc.text = self.cppaid(acppid, arercid, bcppid, brercid)
        self.record_dependency(abxid, 'channel', (acppid, arercid, bcppid, brercid))

    """
    ebMS3 and AS4
    """
    def unify_ebms3_channel(self, acpp, bcpp, abxid,
                            a_channel, b_channel, ebmsbinding,
                            direction):
        (acppid, acid, bcppid, bcid) = abxid

        unify_and_set_att(a_channel, b_channel, ebmsbinding, 'actorOrRole')

        self.unify_as_response(acid, a_channel, bcid, b_channel, ebmsbinding)
        self.unify_channel_descriptions(abxid, a_channel, b_channel, ebmsbinding)

        self.unify_simple_subelement(a_channel, b_channel, ebmsbinding,
                                     'cppa', 'ChannelProfile', required=False)

        logging.info("Unifying ebMS3Channel for {} {}".format(acid, bcid))

        self.unify_mpc(abxid, a_channel, b_channel, ebmsbinding, direction)

        self.unify_simple_subelement(a_channel, b_channel, ebmsbinding,
                                     'cppa', 'SOAPVersion', required=False)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, ebmsbinding,
                                      'cppa', 'Addressing',
                                      self.unify_ws_addressing, direction)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, ebmsbinding,
                                      'cppa', 'WSSecurityBinding',
                                      self.unify_ws_security, direction)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, ebmsbinding,
                                      'cppa', 'AS4ReceptionAwareness',
                                      self.unify_as4_reception_awareness, direction)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, ebmsbinding,
                                      'cppa', 'ErrorHandling',
                                      self.unify_error_handling, direction)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, ebmsbinding,
                                      'cppa', 'ReceiptHandling',
                                      self.unify_receipt_handling, direction)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, ebmsbinding,
                                      'cppa', 'PullChannelId',
                                      self.unify_pull_channel_id, direction)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, ebmsbinding,
                                      'cppa', 'PullHandling',
                                      self.unify_pull_handling, direction)

        self.unify_complex_subelement(acpp, bcpp, abxid, a_channel, b_channel, ebmsbinding,
                                      'cppa', 'AlternateChannel',
                                      self.unify_alternate_channel_id, direction)

        self.unify_transport_elements(acppid, acpp, bcppid, bcpp, a_channel, b_channel,
                                      abxid, ebmsbinding, direction)

        self.unify_package_elements(acppid, acpp, bcppid, bcpp, a_channel, b_channel,
                                    abxid, ebmsbinding, direction)

        logging.info("Unified ebMS3Channel for {} {}".format(acid, bcid))
        return ebmsbinding

    def unify_mpc(self, abxid, a_channel, b_channel, ebmsbinding, direction):
        (acppid, acid, bcppid, bcid) = abxid
        logging.info('Unify MPC for {}, {}'.format(acid, bcid))
        for mpcatt in ['mpc', 'submpcext']:
            ampc = a_channel.get(mpcatt)
            bmpc = b_channel.get(mpcatt)
            a_as_response = a_channel.get('asResponse')
            b_as_response = b_channel.get('asResponse')
            if ampc == bmpc is None:
                pass
            elif ampc == bmpc:
                # MPC specified on both sides with same value:  reuse value
                ebmsbinding.set(mpcatt, ampc)
            elif ampc is not None and bmpc is not None and ampc != bmpc:
                # MPC specified on both sides with conflicting value: unification fails
                raise UnificationException('Incompatible (sub)MPC {}-{} versus {}-{}'.format(acid,
                                                                                             ampc,
                                                                                             bcid,
                                                                                             bmpc))
            else:
                # The MPC is specified on one side only
                logging.info(' {} {} {}'.format(a_as_response, b_as_response, direction))
                if direction == 'send' and xsd_boolean(a_as_response) is not False:
                    # Message is transmitted over backchannel of a Pull request
                    if ampc is not None and bmpc is None:
                        ebmsbinding.set(mpcatt, ampc)
                    else:
                        raise UnificationException('Pull client cannot set (sub)MPC for server {} {}'.format(acid,
                                                                                                             bcid))
                elif direction == 'receive' and xsd_boolean(b_as_response) is not False:
                    # Message is transmitted over backchannel of a Pull request
                    if ampc is None and bmpc is not None:
                        ebmsbinding.set(mpcatt, bmpc)
                    else:
                        raise UnificationException('Pull client cannot set MPC for server {} {}'.format(acid,
                                                                                                        bcid))
                #else:
                #    raise UnificationException('MPC mismatch for {}, {}: {} vs {} '.format(acid,
                #                                                                           bcid,
                #                                                                           ampc,
                #                                                                           bmpc))

    def unify_as_response(self, aid, a_binding, bid, b_binding, ab_binding):
        aval = a_binding.get('asResponse')
        bval = b_binding.get('asResponse')
        if xsd_boolean(aval) is xsd_boolean(bval):
            # both are set with the same Boolean (true or false) value or both are None
            if xsd_boolean(aval) is True:
                # they are set to true
                ab_binding.set('asResponse', 'true')
            else:
                # both are False or None
                # donothing, default is false
                pass

        elif xsd_boolean(aval) is True:
            if xsd_boolean(bval) is None:
                # A is set and is set to true, B is not set
                ab_binding.set('asResponse', 'true')
            else:
                # B is False
                raise UnificationException('Channels {} {} inconsistent for asResponse'.format(aid,
                                                                                               bid))

        elif xsd_boolean(bval) is True:
            if xsd_boolean(aval) is None:
                # B is set and is set to true, A is not set
                ab_binding.set('asResponse', 'true')
            else:
                # A is False
                raise UnificationException('Channels {} {} inconsistent for asResponse'.format(aid,
                                                                                               bid))

    """
    WS-Addressing, for ebMS3 Part 2 multihop feature
    """
    def unify_ws_addressing(self, acpp, bcpp, abxid,
                          a_addressing, b_addressing, ab_addressing, direction):
        self.unify_simple_subelement(a_addressing, b_addressing, ab_addressing,
                                     'cppa', 'Endpoint', required=False)
        self.unify_simple_subelement(a_addressing, b_addressing, ab_addressing,
                                     'cppa', 'Action', required=True, strictatts=True)
        self.unify_complex_subelement(acpp, bcpp, abxid, a_addressing, b_addressing, ab_addressing,
                                      'cppa', 'ebMS3InferredRoutingInput',
                                      self.unify_routinginput, direction)

    def unify_routinginput(self, acpp, bcpp, abxid,
                           a_addressing, b_addressing, ab_addressing, direction):
        self.unify_simple_subelement(a_addressing, b_addressing, ab_addressing,
                                     'cppa', 'ActionSuffix', required=False)
        self.unify_simple_subelement(a_addressing, b_addressing, ab_addressing,
                                     'cppa', 'MPCSuffix', required=False)

    """
    WS-Security
    """
    def unify_ws_security(self, acpp, bcpp, abxid,
                          asec, bsec, security, direction):
        #(acppid, axid, bcppid, bxid) = abxid
        self.unify_simple_subelement(asec, bsec,security, 'cppa', 'WSSVersion', required=False)

        self.unify_simple_subelement(asec, bsec,security, 'cppa', 'SecurityPolicy', required=False)

        self.unify_complex_subelement(acpp, bcpp, abxid, asec, bsec, security,
                                      'cppa', 'SAMLKeyConfirmedSubjectToken',
                                      self.unify_saml_key_confirmed_subject, direction)
        self.unify_complex_subelement(acpp, bcpp, abxid, asec, bsec, security,
                                      'cppa', 'Signature',
                                      self.unify_signature, direction)
        self.unify_complex_subelement(acpp, bcpp, abxid, asec, bsec, security,
                                      'cppa', 'Encryption',
                                      self.unify_encryption, direction)
        self.unify_complex_subelement(acpp, bcpp, abxid, asec, bsec, security,
                                      'cppa', 'UserAuthentication',
                                      self.unify_user_authentication, direction)

    def unify_saml_key_confirmed_subject(self, acpp, bcpp, abxid,
                                               asec, bsec, security, direction):
        (acppid, axid, bcppid, bxid) = abxid
        security.set('id', '{}_{}'.format(asec.get('id'), bsec.get('id')))
        self.unify_simple_subelement(asec, bsec,security, 'cppa', 'SAMLVersion', required=True)
        self.unify_idp_registration_set_ref(acpp, bcpp, abxid,
                                            asec, bsec, security, direction)
        self.include_sender_signing_certificate_ref(acpp, bcpp, abxid,
                                            asec, bsec, security, direction)
        self.unify_saml_attributes(acpp, bcpp, abxid,
                                   asec, bsec, security, direction)
        self.unify_simple_subelement(asec, bsec,security, 'cppa', 'KeyType', required=True)

    def unify_saml_attributes(self, acpp, bcpp, abxid,
                              acppel, bcppel, abcpael, direction):
        if direction is 'send':
            receiver_attributeL = bcppel.xpath(
                'child::cppa:SAMLAttribute',
                namespaces=self.NSMAP
            )
            sender_attributeL = acppel.xpath(
                'child::cppa:SAMLAttribute',
                namespaces=self.NSMAP
            )
        else:
            receiver_attributeL = acppel.xpath(
                'child::cppa:SAMLAttribute',
                namespaces=self.NSMAP
            )
            sender_attributeL = bcppel.xpath(
                'child::cppa:SAMLAttribute',
                namespaces=self.NSMAP
            )
        for receiver_attribute in receiver_attributeL:
            attributename = receiver_attribute.get('Name')
            sender_receiver_match = False
            for sender_attribute in sender_attributeL:
                if sender_attribute.get('Name') == attributename and sender_attribute.get('use') == 'required':
                    sender_receiver_match = True
            if receiver_attribute.get('use') == 'required' and sender_receiver_match is False:
                raise UnificationException(
                    'Required attribute {} not provided by sender'.format(attributename)
                )

    def include_sender_signing_certificate_ref(self, acpp, bcpp, abxid,
                            acppel, bcppel, abcpael, direction):
        if direction == 'send':
            signing_certL = acppel.xpath('child::cppa:SigningCertificateRef',
                                         namespaces=self.NSMAP)
        else:
            signing_certL = bcppel.xpath('child::cppa:SigningCertificateRef',
                                         namespaces=self.NSMAP)
        if len(signing_certL) > 0:
            abcpael.append(deepcopy(signing_certL[0]))

    def unify_idp_registration_set_ref(self, acpp, bcpp, abxid,
                                       acppel, bcppel, abcpael, direction):

        a_idp_set_refL = acppel.xpath('child::cppa:IDPRegistrationSetRef',
                                       namespaces=self.NSMAP)
        b_idp_set_refL = bcppel.xpath('child::cppa:IDPRegistrationSetRef',
                                         namespaces=self.NSMAP)
        if len(a_idp_set_refL) > 0:
            a_idprs_ref = (a_idp_set_refL[0]).get('idpsetid')
            a_idprs = acpp.xpath('descendant::cppa:IDPRegistrationSet[@id="{}"]/cppa:IDPRegistrationRef/@idp'.format(a_idprs_ref),
                                 namespaces=self.NSMAP)

        if len(b_idp_set_refL) > 0:
            b_idprs_ref = (b_idp_set_refL[0]).get('idpsetid')
            b_idprs = bcpp.xpath('descendant::cppa:IDPRegistrationSet[@id="{}"]/cppa:IDPRegistrationRef/@idp'.format(b_idprs_ref),
                                 namespaces=self.NSMAP)

        abcpael.append(deepcopy(b_idp_set_refL[0]))

        idp_sets_intersect = False

        for aidp in a_idprs:
            a_provider = acpp.xpath('descendant::cppa:IDPRegistration[@id="{}"]/cppa:ProviderID/text()'.format(aidp),
                                    namespaces=self.NSMAP)[0]
            logging.info('P: {}'.format(a_provider))
            for bidp in b_idprs:
                b_provider = bcpp.xpath('descendant::cppa:IDPRegistration[@id="{}"]/cppa:ProviderID/text()'.format(bidp),
                                        namespaces=self.NSMAP)[0]
                if a_provider == b_provider:
                    if not idp_sets_intersect:
                        idp_sets_intersect = True
                        provideridel = lxml.etree.SubElement(abcpael, cppa('ProviderID'))
                        provideridel.text = a_provider
                else:
                    logging.info('AIDP {} not found in B')

        if not idp_sets_intersect:
            raise UnificationException('Empty intersection of IDP sets {} and {}'.format(a_idprs_ref,
                                                                                         b_idprs_ref))

        """
        if len(a_signing_certL) == 1 and len(b_signing_anchorL) == 1:
            signingcertid = a_signing_certL[0].get('certId')
            banchorid = b_signing_anchorL[0].get('certId')
            logging.info('Checking if cert {} matches anchors {}'.format(signingcertid,
                                                                         banchorid))
            acert = acpp.xpath('cppa:PartyInfo/cppa:Certificate[@id="{}"]'.format(signingcertid),
                               namespaces=self.NSMAP)[0]
            banchor = bcpp.xpath('cppa:PartyInfo/cppa:TrustAnchor[@id="{}"]'.format(banchorid),
                                 namespaces=self.NSMAP)[0]
            ax509certL = acert.xpath('descendant-or-self::ds:X509Certificate',
                                     namespaces=self.NSMAP)
            rootfound = False
            if len(ax509certL) > 0:
                ax509rootcert = remove_all_whitespace(ax509certL[-1].text)
                logging.debug('Root cert is {} ... {} (len: {})'.format(ax509rootcert[0:6],
                                                                        ax509rootcert[-6:],
                                                                        len(ax509rootcert)))

                for b_anchor_ref in banchor.xpath('cppa:AnchorCertificateRef',
                                               namespaces=self.NSMAP):
                    b_anchor_certid = b_anchor_ref.get('certId')
                    if check_x509_data_content(signingcertid,
                                               ax509rootcert,
                                               b_anchor_certid,
                                               bcpp):
                        rootfound = True
                if not rootfound:
                    for embedded_cert in banchor.xpath('cppa:Certificate',
                                                       namespaces=self.NSMAP):
                        certid = embedded_cert.get('id')
                        if check_x509_data_content(signingcertid,
                                                   ax509rootcert,
                                                   certid,
                                                   bcpp):
                            rootfound = True

            if not rootfound:
                raise UnificationException('Cert {} does not match a root cert in {}'.format(signingcertid,
                                                                                                banchorid))
        else:
            logging.info('No signing anchor/cert specified')
        """


    def unify_signature(self, acpp, bcpp, abxid,
                        asec, bsec, security, direction):
        (acppid, axid, bcppid, bxid) = abxid
        self.unify_simple_subelement(asec, bsec,security,
                                     'cppa', 'SignatureAlgorithm', required=False,
                                     intersectifmultiple=False, strictelements=False)
        self.unify_simple_subelement(asec, bsec,security,
                                     'cppa', 'DigestAlgorithm', required=False,
                                     intersectifmultiple=False, strictelements=False)
        self.unify_simple_subelement(asec, bsec,security,
                                     'cppa', 'SigningCertificateRef', required=False,
                                     strictelements=False, intersectifmultiple=False)
        self.unify_saml_token_ref(acpp, bcpp, abxid, asec, bsec, security, direction)
        self.unify_complex_subelement(acpp, bcpp, abxid, asec, bsec, security,
                                      'cppa', 'SignElements',
                                      self.unify_sign_elements, direction)
        self.unify_boolean_subelement(asec, bsec,security,
                                      'cppa', 'SignAttachments', required=False,
                                      strictelements=True)
        self.unify_boolean_subelement(asec, bsec,security,
                                      'cppa', 'SignExternalPayloads',
                                      required=False, strictelements=True)

        self.unify_signing_cert_and_anchor(acppid, acpp, bcppid, bcpp,
                                           asec, bsec, direction)

    def unify_saml_token_ref(self, acpp, bcpp, abxid,
                            acppel, bcppel, abcpael, direction):
        a_saml_tokenL = acppel.xpath('child::cppa:SAMLTokenRef',
                                       namespaces=self.NSMAP)
        b_saml_tokenL = bcppel.xpath('child::cppa:SAMLTokenRef',
                                         namespaces=self.NSMAP)
        if len(a_saml_tokenL) != len(b_saml_tokenL):
            raise UnificationException('Mismatch in child count for SAMLTokenRef')
        elif len(a_saml_tokenL) == 1:
            a_saml_token_id = (a_saml_tokenL[0]).get('tokenId')
            b_saml_token_id = (b_saml_tokenL[0]).get('tokenId')
            lxml.etree.SubElement(abcpael, cppa('SAMLTokenRef'),
                                  tokenId= '{}_{}'.format(a_saml_token_id,
                                                          b_saml_token_id))


    def unify_sign_elements(self, acpp, bcpp, abxid,
                            asec, bsec, security, direction):
        self.unify_expressions(asec, bsec, security)

    def unify_encryption(self, acpp, bcpp, abxid,
                         asec, bsec, security, direction):
        (acppid, axid, bcppid, bxid) = abxid
        self.unify_complex_subelement(acpp, bcpp, abxid, asec, bsec, security,
                                      'cppa', 'KeyEncryption',
                                      self.unify_key_encryption, direction)
        self.unify_complex_subelement(acpp, bcpp, abxid, asec, bsec, security,
                                      'cppa', 'DataEncryption',
                                      self.unify_data_encryption, direction)
        self.unify_simple_subelement(asec, bsec, security,
                                     'cppa', 'EncryptionCertificateRef',
                                     strictelements=False, required=False)
        self.unify_encryption_cert_and_anchor(acppid, acpp, bcppid, bcpp, asec, bsec, direction)

    def unify_key_encryption(self, acpp, bcpp, abxid,
                             asec, bsec, security, direction):
        self.unify_simple_subelement(asec, bsec,security,
                                     'cppa', 'EncryptionAlgorithm',
                                     required=False,
                                     intersectifmultiple=False, strictelements=False)
        self.unify_simple_subelement(asec, bsec,security,
                                     'cppa', 'MaskGenerationFunction',
                                     required=False,
                                     intersectifmultiple=False, strictelements=False)
        self.unify_simple_subelement(asec, bsec,security,
                                     'cppa', 'DigestAlgorithm',
                                     required=False,
                                     intersectifmultiple=False, strictelements=False)

    def unify_data_encryption(self, acpp, bcpp, abxid,
                              asec, bsec, security, direction):
        self.unify_simple_subelement(asec, bsec,security,
                                     'cppa', 'EncryptionAlgorithm',
                                     required=False,
                                     intersectifmultiple=True, strictelements=False)
        self.unify_complex_subelement(acpp, bcpp, abxid, asec, bsec, security,
                                      'cppa', 'EncryptElements',
                                      self.unify_encrypt_elements, direction)
        self.unify_boolean_subelement(asec, bsec,security,
                                      'cppa', 'EncryptAttachments', required=False,
                                      strictelements=True)
        self.unify_boolean_subelement(asec, bsec,security,
                                      'cppa', 'EncryptExternalPayloads', required=False,
                                      strictelements=True)

    def unify_encrypt_elements(self, acpp, bcpp, abxid,
                               asec, bsec, security, direction):
        self.unify_expressions(asec, bsec, security)

    def unify_expressions(self, asec, bsec, security):
        #(acppid, axid, bcppid, bxid) = abxid
        a_expressions_list = sorted(asec.xpath('child::cppa:Expression/text()',
                                               namespaces=self.NSMAP))
        b_expressions_list = sorted(bsec.xpath('child::cppa:Expression/text()',
                                               namespaces=self.NSMAP))
        if len(a_expressions_list) != len(b_expressions_list):
            return UnificationException('Unequal number of expression in {} {}'.format(acppid,
                                                                                       bcppid))
        else:
            for counter, a_expr in enumerate(a_expressions_list):
                b_expr = b_expressions_list[counter]
                if a_expr != b_expr:
                    raise UnificationException('Mismatch in expression: {} {}'.format(a_expr,
                                                                                      b_expr))
                else:
                    expression = lxml.etree.SubElement(security, cppa('Expression'))
                    expression.text = a_expr

    """
    Reliable Messaging
    """
    def unify_as4_reception_awareness(self, acpp, bcpp, abxid,
                                      ael, bel, abel, direction):
        self.unify_complex_subelement(acpp, bcpp, abxid,
                                      ael, bel, abel,
                                      'cppa', 'DuplicateHandling',
                                      self.unify_duplicate_handling)
        self.unify_retry_handling(acpp, bcpp, abxid,
                                  ael, bel, abel, direction)

    def unify_duplicate_handling(self, acpp, bcpp, abxid,
                                 ael, bel, abel, direction):
        (acppid, axid, bcppid, bxid) = abxid
        self.unify_boolean_subelement(ael, bel,abel,
                                      'cppa', 'DuplicateElimination',
                                      required=True, strictelements=False)
        self.unify_persist_duration(acpp, bcpp, abxid,
                                    ael, bel, abel, direction)

    def unify_persist_duration(self, acpp, bcpp, abxid,
                               ael, bel, abel, direction):
        """
        The PersistDuration of the receiver is used
        """
        (acppid, axid, bcppid, bxid) = abxid
        if direction == "send":
            self.unify_persist_duration_send(acppid, bcppid, ael, bel, abel)
        else:
            self.unify_persist_duration_send(acppid, bcppid, bel, ael, abel)

    def unify_persist_duration_send(self, acppid, bcppid, ael, bel, abel):
        b_persistdurationl = bel.xpath('child::cppa:PersistDuration',
                                       namespaces=self.NSMAP)
        if len(b_persistdurationl) > 0:
            abel.append(self.c14n(deepcopy(b_persistdurationl[0])))

    def unify_retry_handling(self, acpp, bcpp, abxid,
                             ael, bel, abel, direction):
        """
        Retries are handled by the sender, so the configuration for the CPA is
        based on the configuration of the sender.
        @@@ for consideration:  add checks that the last possible retry is within
        the persist duration interval
        """
        (acppid, axid, bcppid, bxid) = abxid
        if direction == "send":
            self.unify_retry_handling_send(acppid, bcppid, ael, bel, abel)
        else:
            self.unify_retry_handling_send(acppid, bcppid, bel, ael, abel)

    def unify_retry_handling_send(self, acppid, bcppid, ael, bel, abel):
        a_RetryHandlingL = ael.xpath('child::cppa:RetryHandling',
                                     namespaces=self.NSMAP)
        if len(a_RetryHandlingL) > 0:
            abel.append(self.c14n(a_RetryHandlingL[0]))

    """
    Error Handling
    """
    def unify_error_handling(self, acpp, bcpp, abxid,
                             ael, bel, parent, direction):
        logging.info("Unifying ErrorHandling for {}".format(ael))

        self.unify_boolean_subelement(ael, bel, parent,
                                      'cppa', 'DeliveryFailuresNotifyProducer',
                                      required = False,
                                      strictelements=False)
        self.unify_boolean_subelement(ael, bel, parent,
                                      'cppa', 'ProcessErrorNotifyConsumer',
                                      required = False,
                                      strictelements = False)
        self.unify_boolean_subelement(ael, bel, parent,
                                      'cppa', 'ProcessErrorNotifyProducer',
                                      required=False,
                                      strictelements=False)

        self.unify_complex_subelement(acpp, bcpp, abxid,
                                      ael, bel, parent,
                                      'cppa', 'ReceiverErrorsReportChannelId',
                                      self.unify_receiver_errors_report_channel_id,
                                      direction)

    def unify_receiver_errors_report_channel_id(self, acpp, bcpp, abxid,
                                                arerc, brerc, abrerc, direction):
        (acppid, axid, bcppid, bxid) = abxid
        logging.info('unify_ReceiverErrorsReportChannelId for {} {}'.format(abxid, arerc))
        arercid = arerc.text
        brercid = brerc.text

        logging.info("Attempting to unify ReceiverErrorsReport channels {} with {}".format(arercid, brercid))
        self.unify_channels((acppid, arercid, bcppid, brercid), acpp, bcpp, None)
        logging.info("Unified ReceiverErrorsReportChannelId {} {}".format(arercid, brercid))
        abrerc.text = self.cppaid(acppid, arercid, bcppid, brercid)

        self.record_dependency(abxid, 'channel', (acppid, arercid, bcppid, brercid))

    """
    Receipt Handling
    """
    def unify_receipt_handling(self, acpp, bcpp, abxid,
                               ael, bel, parent, direction):
        logging.info("Unifying ReceiptHandling for {}".format(ael))
        self.unify_simple_subelement(ael, bel, parent,
                                     'cppa', 'ReceiptFormat',
                                     required=False, strictelements=True,
                                     intersectifmultiple=False)

        self.unify_complex_subelement(acpp, bcpp, abxid, ael, bel, parent,
                                      'cppa', 'ReceiptChannelId',
                                      self.unify_receipt_channel_id, direction)

    def unify_receipt_channel_id(self, acpp, bcpp, abxid,
                                 arerc, brerc, abrerc, direction):
        (acppid, axid, bcppid, bxid) = abxid
        logging.info('unify_ReceiptChannelId for {} {}'.format(abxid, arerc))
        arercid = arerc.text
        brercid = brerc.text
        self.unify_channels((acppid, arercid, bcppid, brercid), acpp, bcpp, None)
        logging.info("Unified ReceiptChannelId {} {}".format(arercid, brercid))
        abrerc.text = self.cppaid(acppid, arercid, bcppid, brercid)
        self.record_dependency(abxid, 'channel', (acppid, arercid, bcppid, brercid))

    """
    self.unify_pull_handling
    """
    def unify_pull_handling(self, acpp, bcpp, abxid,
                            ael, bel, abel, direction):
        (acppid, axid, bcppid, bxid) = abxid
        logging.info('unify_pull_channel_id for {} {}'.format(abxid, ael))

        self.unify_complex_subelement(acpp, bcpp, abxid, ael, bel, abel,
                                      'cppa', 'PullChannelId',
                                      self.unify_pull_channel_id, direction)

    """
    self.unify_pull_channel_id
    """
    def unify_pull_channel_id(self, acpp, bcpp, abxid,
                              ael, bel, abel, direction):
        (acppid, axid, bcppid, bxid) = abxid
        logging.info('unify_pull_channel_id for {} {}'.format(abxid, ael))
        apullchannelid = ael.text
        bpullchannelid = bel.text

        logging.info("Attempting to unify Pull channels {} and {}".format(apullchannelid,
                                                                          bpullchannelid))
        self.unify_channels((acppid, apullchannelid, bcppid, bpullchannelid), acpp, bcpp, None)
        logging.info("Unified PullChannelId {} {}".format(apullchannelid,
                                                          bpullchannelid))
        abel.text = self.cppaid(acppid, apullchannelid, bcppid, bpullchannelid)

        self.record_dependency(abxid, 'channel', (acppid,
                                                  apullchannelid,
                                                  bcppid,
                                                  bpullchannelid))

    """
    self.unify_alternate_channel_id
    """
    def unify_alternate_channel_id(self, acpp, bcpp, abxid,
                                   ael, bel, abel, direction):
        (acppid, axid, bcppid, bxid) = abxid
        logging.info('unify_alternate_channel_id for {} {}'.format(abxid, ael))
        aaltchannelid = ael.text
        baltchannelid = bel.text

        logging.info("Attempting to unify Alternate channels {} and {}".format(aaltchannelid,
                                                                               baltchannelid))
        self.unify_channels((acppid, aaltchannelid, bcppid, baltchannelid), acpp, bcpp, None)
        logging.info("Unified AlternateChannelId {} {}".format(aaltchannelid,
                                                          baltchannelid))
        abel.text = self.cppaid(acppid, aaltchannelid, bcppid, baltchannelid)

        self.record_dependency(abxid, 'channel', (acppid,
                                                  aaltchannelid,
                                                  bcppid,
                                                  baltchannelid))

    """
    Certificates
    """
    def unify_signing_cert_and_anchor(self, acppid, acpp, bcppid, bcpp,
                                      acppel, bcppel, direction):
        if direction == "send":
            self.unify_signing_cert_and_anchor_send(acppid, acpp, bcppid, bcpp,
                                                    acppel, bcppel)
        else:
            self.unify_signing_cert_and_anchor_send(bcppid, bcpp, acppid, acpp,
                                                    bcppel, acppel)

    def unify_signing_cert_and_anchor_send(self, acppid, acpp, bcppid, bcpp,
                                           acppel, bcppel):
        a_signing_certL = acppel.xpath('child::cppa:SigningCertificateRef',
                                       namespaces=self.NSMAP)
        b_signing_anchorL = bcppel.xpath('child::cppa:SigningTrustAnchorRef',
                                         namespaces=self.NSMAP)
        if len(a_signing_certL) == 1 and len(b_signing_anchorL) == 1:
            signingcertid = a_signing_certL[0].get('certId')
            banchorid = b_signing_anchorL[0].get('certId')
            logging.info('Checking if cert {} matches anchors {}'.format(signingcertid,
                                                                         banchorid))
            acert = acpp.xpath('cppa:PartyInfo/cppa:Certificate[@id="{}"]'.format(signingcertid),
                               namespaces=self.NSMAP)[0]
            banchor = bcpp.xpath('cppa:PartyInfo/cppa:TrustAnchor[@id="{}"]'.format(banchorid),
                                 namespaces=self.NSMAP)[0]
            ax509certL = acert.xpath('descendant-or-self::ds:X509Certificate',
                                     namespaces=self.NSMAP)
            rootfound = False
            if len(ax509certL) > 0:
                ax509rootcert = remove_all_whitespace(ax509certL[-1].text)
                logging.debug('Root cert is {} ... {} (len: {})'.format(ax509rootcert[0:6],
                                                                        ax509rootcert[-6:],
                                                                        len(ax509rootcert)))

                for b_anchor_ref in banchor.xpath('cppa:AnchorCertificateRef',
                                               namespaces=self.NSMAP):
                    b_anchor_certid = b_anchor_ref.get('certId')
                    if check_x509_data_content(signingcertid,
                                               ax509rootcert,
                                               b_anchor_certid,
                                               bcpp):
                        rootfound = True
                if not rootfound:
                    for embedded_cert in banchor.xpath('cppa:Certificate',
                                                       namespaces=self.NSMAP):
                        certid = embedded_cert.get('id')
                        if check_x509_data_content(signingcertid,
                                                   ax509rootcert,
                                                   certid,
                                                   bcpp):
                            rootfound = True

            if not rootfound:
                raise UnificationException('Cert {} does not match a root cert in {}'.format(signingcertid,
                                                                                                banchorid))
        else:
            logging.info('No signing anchor/cert specified')

    def unify_encryption_cert_and_anchor(self, acppid, acpp, bcppid, bcpp,
                                         acppel, bcppel, direction):
        if direction == "send":
            self.unify_encryption_cert_and_anchor_send(acppid, acpp, bcppid, bcpp,
                                                       acppel, bcppel)
        else:
            self.unify_encryption_cert_and_anchor_send(bcppid, bcpp, acppid, acpp,
                                                       bcppel, acppel)

    def unify_encryption_cert_and_anchor_send(self, acppid, acpp, bcppid, bcpp,
                                              acppel, bcppel):
        a_encryption_anchorL = acppel.xpath('child::cppa:EncryptionTrustAnchorRef',
                                            namespaces=self.NSMAP)
        b_encryption_certL = bcppel.xpath('child::cppa:EncryptionCertificateRef',
                                          namespaces=self.NSMAP)
        if len(a_encryption_anchorL) == 1 and len(b_encryption_certL) == 1:
            aanchorid = a_encryption_anchorL[0].get('certId')
            encryptioncertid = b_encryption_certL[0].get('certId')
            logging.info('Checking if cert {} matches anchors {}'.format(encryptioncertid,
                                                                         aanchorid))

            aanchor = acpp.xpath('cppa:PartyInfo/cppa:TrustAnchor[@id="{}"]'.format(aanchorid),
                                 namespaces=self.NSMAP)[0]
            bcert = bcpp.xpath('cppa:PartyInfo/cppa:Certificate[@id="{}"]'.format(encryptioncertid),
                               namespaces=self.NSMAP)[0]

            bx509certl = bcert.xpath('descendant-or-self::ds:X509Certificate',
                                     namespaces=self.NSMAP)
            if len(bx509certl) > 0:
                bx509rootcert = remove_all_whitespace(bx509certl[-1].text)
                logging.debug('Root cert is {} ... {} (len: {})'.format(bx509rootcert[0:6],
                                                                        bx509rootcert[-6:],
                                                                        len(bx509rootcert)))
                rootfound = False
                for a_anchor_ref in aanchor.xpath('cppa:AnchorCertificateRef',
                                               namespaces=self.NSMAP):
                    a_anchor_certid = a_anchor_ref.get('certId')
                    if check_x509_data_content(encryptioncertid, bx509rootcert, a_anchor_certid, acpp):
                        rootfound = True
                if not rootfound:
                    for embedded_cert in aanchor.xpath('cppa:Certificate', namespaces=self.NSMAP):
                        certid = embedded_cert.get('id')
                        if check_x509_data_content(encryptioncertid, bx509rootcert, certid, acpp):
                            rootfound = True

                """
                bx509rootcert = bx509certl[-1].text

                bx509rootcert = remove_all_whitespace(bx509certl[-1].text)
                logging.debug('Root cert is {} ... {} (len: {})'.format(bx509rootcert[0:6],
                                                                        bx509rootcert[-6:],
                                                                        len(bx509rootcert)))

                rootfound = False

                for a_anchor_ref in aanchor.xpath('cppa:AnchorCertificateRef',
                                               namespaces=self.NSMAP):
                    a_anchor_certid = a_anchor_ref.get('certId')
                    a_anchor_cert = acpp.xpath('descendant::cppa:Certificate[@id="{}"]'.format(a_anchor_certid),
                                               namespaces=self.NSMAP)[0]
                    a_anchor_cert_data = a_anchor_cert.xpath('descendant::ds:X509Certificate/text()',
                                                             namespaces=self.NSMAP)[0]
                    a_anchor_cert_data = remove_all_whitespace(a_anchor_cert_data)

                    logging.debug('Comparing against {} {} ... {} (len: {})'.format(a_anchor_certid,
                                                                                    a_anchor_cert_data[0:6],
                                                                                    a_anchor_cert_data[-6:],
                                                                                    len(a_anchor_cert_data)))
                    if str(bx509rootcert) == str(a_anchor_cert_data):
                        logging.info('Referenced X509Certificate found in anchor {} cert {}'.format(a_anchor_ref,
                                                                                                    a_anchor_certid))


                        rootfound = True

                """
                if not rootfound:
                    raise UnificationException('Cert {} does not match a root cert in {}'.format(encryptioncertid,
                                                                                                 aanchorid))

        else:
            logging.info('No encryption anchor/cert specified')

    """
    User Authentication

    A username and password are generated as part of CPA formation
    """

    def unify_user_authentication(self, acpp, bcpp, abxid,
                                  ael, bel, abel, direction):
        (acppid, aelid, bcppid, belid) = abxid
        usernameel = lxml.etree.SubElement(abel, cppa('Username'))
        usernameel.text = create_username(acppid, aelid, bcppid, belid)
        passwordel = lxml.etree.SubElement(abel, cppa('Password'))
        passwordel.text = create_random_password()
        self.unify_boolean_subelement(ael, bel, abel,
                                      'cppa', 'Digest', required=False)
        self.unify_boolean_subelement(ael, bel, abel,
                                      'cppa', 'Nonce', required=False)
        self.unify_boolean_subelement(ael, bel, abel,
                                      'cppa', 'Created', required=False)

    """
    Transport
    """
    def unify_transport_elements(self, acppid, acpp, bcppid, bcpp,
                                 a_channel, b_channel, abxid, binding,
                                 direction):
        atid = a_channel.get('transport')
        btid = b_channel.get('transport')
        if atid is not None and btid is not None:
            self.unify_transport(acppid, acpp,
                                 bcppid, bcpp,
                                 atid,
                                 btid,
                                 direction)

            abtid = self.cppaid(acppid, atid, bcppid, btid)
            binding.set('transport', abtid)
            self.record_dependency(abxid, 'transport', (acppid, atid, bcppid, btid))
        elif (atid is None and btid is not None) or (btid is None and atid is not None):
            raise UnificationException('Element {} and {} inconsistent for transport'.format(a_channel.get('id'),
                                                                                             b_channel.get('id')))

    def unify_transport(self, acppid, acpp, bcppid, bcpp,
                        atid, btid, direction):
        cached, result = self.memo(acppid,
                                   atid,
                                   bcppid,
                                   btid,
                                   self.unify_transport_results,
                                   self.unify_transport_exceptions)
        if cached:
            return result
        try:
            result = self.unify_transport_memo(acppid, acpp, bcppid, bcpp,
                                               atid, btid, direction)
        except UnificationException as e:
            self.unify_transport_exceptions[acppid, atid, bcppid, btid] = e
            raise
        else:
            self.unify_transport_results[acppid, atid, bcppid, btid] = result
            return result

    def unify_transport_memo(self, acppid, acpp, bcppid, bcpp,
                             atid, btid, direction):
        try:
            if atid is None and btid is None:
                logging.info("No transport, OK")
                return (acppid, bcppid, atid, btid)
            elif atid is None or btid is None:
                raise Exception('Missing transport {} or {}'.format(atid, btid))
            else:
                atransport = acpp.xpath('descendant::node()[@id="{}"]'.format(atid),
                                        namespaces=self.NSMAP)[0]
                btransport = bcpp.xpath('descendant::node()[@id="{}"]'.format(btid),
                                        namespaces=self.NSMAP)[0]
                if atransport.tag != btransport.tag:
                    raise UnificationException('Mismatch in transport type: {} vs {}'.format(atransport.tag,
                                                                                             btransport.tag))
                transportxml = lxml.etree.Element(atransport.tag, id=self.cppaid(acppid,
                                                                                 atransport.get('id'),
                                                                                 bcppid,
                                                                                 btransport.get('id')),
                                                   nsmap=self.NSMAP)
                description = lxml.etree.SubElement(transportxml, cppa('Description'))
                description.set(xml('lang'),'en')
                description.text = 'Transport formed from {} in {} and {} in {}'.format(atid,
                                                                                        acppid,
                                                                                        btid,
                                                                                        bcppid)

                self.unify_simple_subelement(atransport, btransport, transportxml,
                                             'cppa', 'ClientIPv4',
                                             required=False, strictelements=False,
                                             intersectifmultiple=False)
                self.unify_simple_subelement(atransport, btransport, transportxml,
                                             'cppa', 'ClientIPv6',
                                             required=False, strictelements=False)
                self.unify_simple_subelement(atransport, btransport, transportxml,
                                             'cppa', 'Endpoint',
                                             required=False, strictelements=False)
                self.unify_complex_subelement(acpp, bcpp, (acppid, atid, bcppid, btid), atransport, btransport,
                                              transportxml,
                                              'cppa', 'TransportLayerSecurity',
                                              self.unify_transport_layer_security, direction)
                self.unify_complex_subelement(acpp, bcpp, (acppid, atid, bcppid, btid), atransport, btransport,
                                              transportxml,
                                              'cppa', 'UserAuthentication',
                                              self.unify_user_authentication, direction)

                return transportxml
        except UnificationException as e:
            raise UnificationException('Transport {} {}: {}'.format(atid, btid, e))

    def unify_transport_layer_security(self, acpp, bcpp, abxid,
                                       atls, btls, abtls, direction):
        if direction == "send":
            self.unify_transport_layer_security_send(acpp, bcpp, abxid,
                                                     atls, btls, abtls)
        else:
            self.unify_transport_layer_security_send(bcpp, acpp, abxid,
                                                     btls, atls, abtls)

    def unify_transport_layer_security_send(self, acpp, bcpp, abxid,
                                            atls, btls, abtls):
        (acppid, axid, bcppid, bxid) = abxid
        logging.info('Unifying TransportLayerSecurity for {} {}'.format(axid,
                                                                        bxid))
        self.unify_simple_subelement(atls, btls, abtls,
                                     'cppa', 'TLSProtocol',
                                     required=False, strictelements=False)
        self.unify_simple_subelement(atls, btls, abtls,
                                     'cppa', 'CipherSuite',
                                     required=False,
                                     intersectifmultiple=True,
                                     strictelements=False)
        self.unify_simple_subelement(atls, btls, abtls,
                                     'cppa', 'ClientCertificateRef',
                                     required=False, strictelements=False)
        self.unify_simple_subelement(atls, btls, abtls,
                                     'cppa', 'ServerCertificateRef',
                                     required=False, strictelements=False)

        self.unify_tls_server_cert_and_anchor_send(acppid, acpp, bcppid, bcpp,
                                                   atls, btls)
        self.unify_tls_client_cert_and_anchor_send(acppid, acpp, bcppid, bcpp,
                                                   atls, btls)

    def unify_tls_server_cert_and_anchor_send(self, acppid, acpp, bcppid, bcpp,
                                              atls, btls):
        a_server_anchorL = atls.xpath('child::cppa:ServerTrustAnchorRef',
                                            namespaces=self.NSMAP)
        b_server_certL = btls.xpath('child::cppa:ServerCertificateRef',
                                          namespaces=self.NSMAP)
        if len(a_server_anchorL) == 1 and len(b_server_certL) == 1:
            aanchorid = a_server_anchorL[0].get('certId')
            server_certid = b_server_certL[0].get('certId')
            logging.info('Checking if cert {} matches anchors {}'.format(server_certid,
                                                                         aanchorid))
            aanchor = acpp.xpath('cppa:PartyInfo/cppa:TrustAnchor[@id="{}"]'.format(aanchorid),
                                 namespaces=self.NSMAP)[0]
            bcert = bcpp.xpath('cppa:PartyInfo/cppa:Certificate[@id="{}"]'.format(server_certid),
                               namespaces=self.NSMAP)[0]

            bx509certL = bcert.xpath('descendant-or-self::ds:X509Certificate',
                                     namespaces=self.NSMAP)
            if len(bx509certL) > 0:
                bx509rootcert = bx509certL[-1].text
                rootfound = False
                for arootcert in aanchor.xpath('cppa:Certificate',
                                               namespaces=self.NSMAP):
                    arootcertid = arootcert.get('id')
                    if arootcert.xpath('descendant::ds:X509Certificate/text()="{}"'.format(bx509rootcert),
                                       namespaces=self.NSMAP):
                        logging.info('Referenced X509Certificate found in anchor {} cert {}'.format(aanchorid,
                                                                                                    arootcertid))
                        rootfound = True
                if not rootfound:
                    raise UnificationException('Cert {} does not match a root cert in {}'.format(server_certid,
                                                                                             aanchorid))
        else:
            logging.info('No encryption anchor/cert specified')

    def unify_tls_client_cert_and_anchor_send(self, acppid, acpp, bcppid, bcpp,
                                              atls, btls):
        a_client_certL = atls.xpath('child::cppa:ClientCertificateRef',
                                    namespaces=self.NSMAP)
        b_client_anchorL = btls.xpath('child::cppa:ClientTrustAnchorRef',
                                      namespaces=self.NSMAP)
        if len(b_client_anchorL) == 1 and len(a_client_certL) == 1:
            banchorid = b_client_anchorL[0].get('certId')
            client_certid = a_client_certL[0].get('certId')
            logging.info('Checking if cert {} matches anchors {}'.format(client_certid,
                                                                         banchorid))
            acert = acpp.xpath('cppa:PartyInfo/cppa:Certificate[@id="{}"]'.format(client_certid),
                               namespaces=self.NSMAP)[0]
            banchor = bcpp.xpath('cppa:PartyInfo/cppa:TrustAnchor[@id="{}"]'.format(banchorid),
                                 namespaces=self.NSMAP)[0]

            ax509certL = acert.xpath('descendant-or-self::ds:X509Certificate',
                                     namespaces=self.NSMAP)
            if len(ax509certL) > 0:
                ax509rootcert = ax509certL[-1].text
                rootfound=False
                for arootcert in banchor.xpath('cppa:Certificate',
                                               namespaces=self.NSMAP):
                    arootcertid = arootcert.get('id')
                    if arootcert.xpath('descendant::ds:X509Certificate/text()="{}"'.format(ax509rootcert),
                                       namespaces=self.NSMAP):
                        logging.info('Referenced X509Certificate found in anchor {} cert {}'.format(banchorid,
                                                                                                    arootcertid))
                        rootfound=True
            if not(rootfound):
                raise UnificationException('Cert {} does not match a root cert in {}'.format(client_certid,
                                                                                             banchorid))
        else:
            logging.info('No encryption anchor/cert specified')

    """
    Properties

    Unify properties in two action bindings.

    Checks that the two bindings have the same number of properties and that they
    match pairwise.

    """

    def unify_properties(self, aid, acpp, a_binding,
                         bid, bcpp, b_binding, actionbinding):

        if a_binding.get('propertySetId') == b_binding.get('propertySetId') == None:
            a_property_list = a_binding.xpath('child::cppa:Property',
                                             namespaces=self.NSMAP)
            b_property_list = b_binding.xpath('child::cppa:Property',
                                             namespaces=self.NSMAP)
            b_parent = b_binding
        else:
            if a_binding.get('propertySetId') != None:
                a_property_list = acpp.xpath(
                    "cppa:PropertySet[@id='{}']/child::cppa:Property".format(
                        a_binding.get('propertySetId')),
                    namespaces=self.NSMAP)
            else:
                a_property_list = a_binding.xpath('child::cppa:Property',
                                                 namespaces=self.NSMAP)
            if b_binding.get('propertySetId') != None:
                b_property_list = bcpp.xpath(
                    "cppa:PropertySet[@id='{}']/child::cppa:Property".format(
                        b_binding.get('propertySetId')),
                    namespaces=self.NSMAP)
                b_parent = bcpp.xpath(
                    "cppa:PropertySet[@id='{}']".format(b_binding.get('propertySetId')),
                    namespaces=self.NSMAP)[0]
            else:
                b_property_list = b_binding.xpath('child::cppa:Property',
                                                 namespaces=self.NSMAP)
                b_parent = b_binding
        if len(a_property_list) != len(b_property_list):
            raise UnificationException('Unequal number of properties for {}, {}'.format(aid, bid))
        else:
            xpq = 'child::cppa:Property[@name="{}" and @minOccurs="{}" and @maxOccurs="{}"]'
            for aprop in a_property_list:
                aname = aprop.get('name')
                a_min = aprop.get('minOccurs')
                a_max = aprop.get('maxOccurs')
                bpropl = b_parent.xpath(xpq.format(aname,a_min,a_max),
                                        namespaces=self.NSMAP)
                if len(bpropl) == 0:
                    raise UnificationException('Mismatch for property {} in {}, {}'.format(aname,
                                                                                           aid,
                                                                                           bid))
                else:
                    actionbinding.append(deepcopy(aprop))


    def inline_property_set_references(self, action_binding):
        pass

    """
    Payload Profiles
    """
    def unify_payload_profile(self, acppid, acpp, bcppid, bcpp,
                              aid, bid):
        logging.info('Unifying payload profiles {} {} and {} {}'.format(acppid,
                                                                        aid,
                                                                        bcppid,
                                                                        bid))
        cached, result = self.memo(acppid,
                                   aid,
                                   bcppid,
                                   bid,
                                   self.unify_payload_profile_results,
                                   self.unify_payload_profile_exceptions)
        if cached:
            return result
        try:
            result = self.unify_payload_profile_memo(acppid, acpp, bcppid, bcpp, aid, bid)
        except UnificationException as e:
            self.unify_payload_profile_exceptions[acppid, aid, bcppid, bid] = e
            raise
        else:
            self.unify_payload_profile_results[acppid, aid, bcppid, bid] = result
            return result

    def unify_payload_profile_memo(self, acppid, acpp, bcppid, bcpp,
                                   aid, bid):
        try:
            if aid == bid is None:
                logging.info("No payload profile, OK")
                return None
            elif aid is None or bid is None:
                raise Exception('Missing payload profile {} or {}'.format(aid, bid))
            else:
                app = acpp.xpath('descendant::node()[@id="{}"]'.format(aid),
                                        namespaces=self.NSMAP)[0]
                bpp = bcpp.xpath('descendant::node()[@id="{}"]'.format(bid),
                                        namespaces=self.NSMAP)[0]

                abpp = lxml.etree.Element(app.tag, id=self.cppaid(acppid,
                                                                  app.get('id'),
                                                                  bcppid,
                                                                  bpp.get('id')),
                                                   nsmap=self.NSMAP)

                #self.unify_payload_parts(acppid, aid, app, bcppid, bid, bpp, abpp)
                self.unify_payload_parts(acpp, bcpp, acppid, aid, app, bcppid, bid, bpp, abpp)
                return abpp

        except UnificationException as e:
            raise UnificationException('Payload Profile {} {}: {}'.format(aid, bid, e))

    def unify_payload_parts(self, acpp, bcpp, acppid, appid, app, bcppid, bppid, bpp, abpp):
        app_part_list = app.xpath('child::cppa:PayloadPart',
                                  namespaces=self.NSMAP)
        bpp_part_list = bpp.xpath('child::cppa:PayloadPart',
                                  namespaces=self.NSMAP)
        alen = len(app_part_list)
        blen = len(bpp_part_list)
        if alen != blen:
            raise UnificationException('Inconsistent number of payload parts {} {}: {}; {} {}: {}'.format(acppid,
                                                                                                          appid,
                                                                                                          alen,
                                                                                                          bcppid,
                                                                                                          bppid,
                                                                                                          blen))
        else:
            for c in range(0,alen):
                appart = app_part_list[c]
                bppart = bpp_part_list[c]
                self.unify_payload_part(acpp,
                                        bcpp,
                                        acppid,
                                        appid,
                                        appart,
                                        bcppid,
                                        bppid,
                                        bppart,
                                        c,
                                        abpp)

    def unify_payload_part(self, acpp, bcpp, acppid, appid, appart, bcppid,
                           bppid, bppart, c, abpp):
        abpart = lxml.etree.Element(appart.tag)
        unify_cardinality(appart, bppart, abpart, '{} {} {}'.format(appid, bppid, c))
        unify_atts(appart, bppart, abpart, False, ['requireSignature',
                                                   'requireEncryption'])
        self.unify_simple_subelement(appart, bppart, abpart,
                                     'cppa', 'PartName')
        self.unify_simple_subelement(appart, bppart, abpart,
                                     'cppa', 'MIMEContentType',
                                     required=False, strictelements=False)
        self.unify_simple_subelement(appart, bppart, abpart,
                                     'cppa', 'Schema', required=False,
                                     strictelements=False, intersectifmultiple=True)
        self.unify_complex_subelement(acpp, bcpp,
                                      (acppid, appid, bcppid, bppid),
                                      appart,
                                      bppart,
                                      abpart,
                                      'cppa', 'Signature',
                                      self.unify_signature, None)
        self.unify_complex_subelement(acpp, bcpp,
                                      (acppid, appid, bcppid, bppid),
                                      appart,
                                      bppart,
                                      abpart,
                                      'cppa', 'Encryption',
                                      self.unify_encryption, None)
        abpp.append(abpart)

    """
    Packaging
    """
    def unify_package_elements(self, acppid, acpp, bcppid, bcpp,
                               a_channel, b_channel,
                               abxid,
                               ebmsbinding, direction):
        apid = a_channel.get('package')
        bpid = b_channel.get('package')

        if apid is not None and bpid is not None:
            self.unify_package(acppid, acpp,
                               bcppid, bcpp,
                               apid, bpid,
                               abxid,
                               direction)
            abpid = self.cppaid(acppid, apid, bcppid, bpid)
            ebmsbinding.set('package', abpid)
            self.record_dependency(abxid, 'package', (acppid, apid, bcppid, bpid))

    def unify_package(self, acppid, acpp,
                      bcppid, bcpp,
                      apid, bpid,
                      abxid,
                      direction):
        cached, result = self.memo(acppid,
                                   apid,
                                   bcppid,
                                   bpid,
                                   self.unify_package_results,
                                   self.unify_package_exceptions)
        if cached:
            return result
        try:
            result = self.unify_package_memo(acppid, acpp, bcppid, bcpp,
                                             apid, bpid, abxid, direction)
        except UnificationException as e:
            self.unify_package_exceptions[acppid, apid, bcppid, bpid] = e
            raise
        else:
            self.unify_package_results[acppid, apid, bcppid, bpid] = result
            return result

    def unify_package_memo(self, acppid, acpp, bcppid, bcpp,
                           apid, bpid, abxid, direction):
        try:
            if apid == bpid is None:
                logging.info("No packaging, OK")
                return None
            elif apid is None or bpid is None:
                raise Exception('Missing package {} or {}'.format(apid, bpid))
            else:
                logging.info('Attempting to unify packages {} and {}'.format(apid,
                                                                            bpid))
                apackage = acpp.xpath('descendant::node()[@id="{}"]'.format(apid),
                                        namespaces=self.NSMAP)[0]
                bpackage = bcpp.xpath('descendant::node()[@id="{}"]'.format(bpid),
                                        namespaces=self.NSMAP)[0]

                if apackage.tag != bpackage.tag:
                    raise UnificationException('Incompatible package types {} {}'.format(apackage.tag,
                                                                                         bpackage.tag))
                elif apackage.tag not in self.packaging_handlers:
                    raise UnificationException('Unsupported package type {} {}'.format(apackage.tag,
                                                                                       bpackage.tag))
                else:
                    try:
                        handler = self.packaging_handlers[apackage.tag]
                        logging.info("Package compatible {} {}".format(apid, bpid))
                        return handler(acpp, acppid, bcpp, bcppid, apackage, bpackage, abxid, direction)
                    except UnificationException as e:
                        raise UnificationException('Mismatch in package {}: {}'.format(apackage.tag,
                                                                                       e))

        except UnificationException as e:
            raise UnificationException('Transport {} {}: {}'.format(apid, bpid, e.value))

    """
    @@@TODO merge the following
    """
    def unify_soap_with_attachments_envelope(self, acpp, acppid, bcpp, bcppid,
                                             apackage, bpackage, abxid, direction):
        swael = lxml.etree.Element(apackage.tag, nsmap=self.NSMAP)
        self.unify_mime_part_lists(swael, apackage, bpackage, abxid, acpp, bcpp, direction)
        return swael

    def unify_simple_soap_envelope(self, acpp, acppid, bcpp, bcppid,
                                   apackage, bpackage, abxid, direction):
        sel = lxml.etree.Element(apackage.tag, nsmap=self.NSMAP)
        self.unify_mime_part_lists(sel, apackage, bpackage, abxid, acpp, bcpp, direction)
        return sel

    def unify_mime_envelope(self, acpp, acppid, bcpp, bcppid,
                            apackage, bpackage, abxid, direction):
        sel = lxml.etree.Element(apackage.tag, nsmap=self.NSMAP)
        self.unify_mime_part_lists(mimepart, apart, bpart, abxid, acpp, bcpp, direction)
        return sel

    def unify_compressed_mime_part(self, apart, bpart, abxid,
                                   acpp, bcpp, direction):
        mimepart = lxml.etree.Element(apart.tag, nsmap=self.NSMAP)
        unify_atts(apart, bpart, mimepart, strictatts=True)
        self.unify_mime_part_lists(mimepart, apart, bpart, abxid, acpp, bcpp, direction)
        return mimepart

    def unify_mime_multipart_related(self, apart, bpart, abxid,
                                     acpp, bcpp, direction):
        mimepart = lxml.etree.Element(apart.tag, nsmap=self.NSMAP)
        unify_atts(apart, bpart, mimepart, strictatts=True)
        self.unify_mime_part_lists(mimepart, apart, bpart, abxid,
                                   acpp, bcpp, direction)
        return mimepart

    def unify_simple_mime_part(self, apart, bpart, abxid,
                               acpp, bcpp, direction):
        mimepart = lxml.etree.Element(apart.tag, nsmap=self.NSMAP)
        aname = apart.get('PartName')
        bname = bpart.get('PartName')
        if aname != bname:
            raise UnificationException('Incompatible PartName {} vs {}'.format(aname,
                                                                               bname))
        else:
            mimepart.set('PartName',aname)
            return mimepart

    def unify_external_payload(self, apart, bpart, abxid, acpp, bcpp, direction):
        mimepart = lxml.etree.Element(apart.tag, nsmap=self.NSMAP)
        aname = apart.get('PartName')
        bname = bpart.get('PartName')
        if aname != bname:
            raise UnificationException('Incompatible PartName {} vs {}'.format(aname,
                                                                               bname))
        else:
            (acppid, axid, bcppid, bxid) = abxid
            mimepart.set('PartName',aname)
            a_ep_ch_id = apart.xpath('child::cppa:ChannelId/text()',
                                     namespaces=self.NSMAP)[0]
            b_ep_ch_id = bpart.xpath('child::cppa:ChannelId/text()',
                                     namespaces=self.NSMAP)[0]
            transportchannelid = (acppid, a_ep_ch_id, bcppid, b_ep_ch_id)
            self.unify_channels(transportchannelid, acpp, bcpp, direction)
            self.record_dependency(abxid, 'channel', transportchannelid)

            abchannel = lxml.etree.SubElement(mimepart, cppa('ChannelId'))
            abchannel.text = self.cppaid(acppid, a_ep_ch_id, bcppid, b_ep_ch_id)
            return mimepart

    def unify_mime_part_lists(self, parent, apackage, bpackage, abxid,
                              acpp, bcpp, direction):
        apartl = apackage.xpath('child::*[local-name()!="Description"]')
        bpartl = bpackage.xpath('child::*[local-name()!="Description"]')
        alen, blen = len(apartl), len(bpartl)
        if alen != blen:
            raise UnificationException('Mismatch in child count for package: {} {}'.format(alen,
                                                                                           blen))
        else:
            for apart, bpart in zip(apartl, bpartl):
                if apart.tag != bpart.tag:
                    raise UnificationException('Mismatch in child type for package: {} {}'.format(alen,
                                                                                                  blen))
                else:
                    handler = self.mimepart_handlers[apart.tag]
                    parent.append(handler(apart, bpart, abxid, acpp, bcpp, direction))
                    logging.info('### Adding {}'.format(apart))

    """
    Auxiliary functions
    """
    def memo(self, p1, p2, p3, p4, results, exceptions):
        if (p1, p2, p3, p4) in results:
            logging.info("Results cache hit for {} {} {} {}".format(p1, p2, p3, p4))
            return True, results[p1, p2, p3, p4]
        elif (p1, p2, p3, p4) in exceptions:
            logging.info("Exceptions cache hit for {} {}".format(p1, p2, p3, p4))
            raise exceptions[p1, p2, p3, p4]
        else:
            return False, None

    def confirm_included(self, componenttype, id):
        if not componenttype in self.included_components:
            self.included_components[componenttype] = []
        if not id in self.included_components[componenttype]:
            self.included_components[componenttype].append(id)

    def record_dependency(self, source, category, target):
        if not source in self.depends_on:
            self.depends_on[source] = {}
        if not category in self.depends_on[source]:
            self.depends_on[source][category] = [target]
            logging.info("Dependency {} {} {} created".format(source,
                                                              category,
                                                              target))
        targetlist = self.depends_on[source][category]
        if target not in targetlist:
            logging.info("Dependency {} {} {} added to list".format(source,
                                                                    category,
                                                                    target))
            targetlist.append(target)
        else:
            logging.info("Dependency {} {} {} already on list".format(source,
                                                                      category,
                                                                      target))

    def unify_simple_subelement(self, ael, bel, abel, childns, childtag,
                                required=True,
                                strictelements=True,
                                strictatts=True,
                                boolean=False,
                                intersectifmultiple=False):
        """
        strictelements:  either both inputs have the subelement or sequence of subelements or none
        required:  there must be at least one match
        intersectifmultiple:  if both inputs may have multiple elements, the unification is
        their intersection if True; if False, there must be a one-to-one unification of subelement
        instances.
        strictatts:  if one input has an attribute then the other must have it too with same value
        boolean:  if the value is Boolean
        """
        logging.info("Unifying subelement {} for {}".format(childtag, abel.tag))
        try:
            achildren = ael.xpath('child::{}:{}'.format(childns, childtag),
                                namespaces=self.NSMAP)
            bchildren = bel.xpath('child::{}:{}'.format(childns, childtag),
                                namespaces=self.NSMAP)

            achildcount = len(achildren)
            bchildcount = len(bchildren)

            at_least_one_shared_child_matches = False

            if strictelements and achildcount != bchildcount:
                raise UnificationException('Child count mismatch for {}: {}, {}'.format(childtag,
                                                                                        achildcount,
                                                                                        bchildcount))
            elif achildcount == 0 and bchildcount == 0 and required:
                raise UnificationException('Missing child {} {} {}'.format(childtag,
                                                                           achildcount,
                                                                           bchildcount))

            elif achildcount == 0 and bchildcount > 0:
                for bchild in bchildren:
                    abchild = lxml.etree.Element(ns(self.NSMAP[childns], childtag),
                                                 nsmap=self.NSMAP)
                    abchild.text = bchild.text
                    copy_atts(bchild,abchild)
                    abel.append(abchild)
                #at_least_one_shared_child_matches = True
            elif achildcount >  0 and bchildcount == 0:
                for achild in achildren:
                    abchild = lxml.etree.Element(ns(self.NSMAP[childns], childtag),
                                                 nsmap=self.NSMAP)
                    abchild.text = achild.text
                    copy_atts(achild,abchild)
                    abel.append(abchild)
                #at_least_one_shared_child_matches = True
            elif achildcount == 0 and bchildcount > 0:
                for bchild in bchildren:
                    abchild = lxml.etree.Element(ns(self.NSMAP[childns], childtag),
                                                 nsmap=self.NSMAP)
                    abchild.text = achild.text
                    copy_atts(achild,abchild)
                    abel.append(abchild)
                #at_least_one_shared_child_matches = True
            elif achildcount == 1 and bchildcount == 1:
                abchild = lxml.etree.Element(ns(self.NSMAP[childns], childtag),
                                             nsmap=self.NSMAP)
                abchild.text = unify_boolean_or_text(achildren[0],
                                                     bchildren[0],
                                                     boolean)
                unify_atts(achildren[0], bchildren[0],abchild,
                           strictatts=strictatts)
                abel.append(abchild)
                #at_least_one_shared_child_matches = True
            elif achildcount >= 1 and bchildcount >= 1:
                #if bchildcount > achildcount and not intersectifmultiple:
                #    raise UnificationException('Too many {} nodes, {} vs {}'.format(childtag,
                #                                                                    bchildcount,
                #                                                                    achildcount))

                for counter, achild in enumerate(achildren, 1):
                    bchildmatchfound = False
                    for bchild in bchildren:
                        try:
                            abchild = lxml.etree.Element(ns(self.NSMAP[childns], childtag),
                                                         nsmap=self.NSMAP)
                            abchild.text = unify_boolean_or_text(achild,
                                                                 bchild,
                                                                 boolean)
                            unify_atts(achild, bchild, abchild,
                                       strictatts=strictatts)

                        except UnificationException as e:
                            logging.info("Skipping non-matching {} #{}, suppressing {}".format(achild.tag,
                                                                                               counter,
                                                                                               e.value))
                        else:
                            logging.info("Matched {} #{}".format(achild.tag, counter))
                            abel.append(abchild)
                            bchildmatchfound = True
                            at_least_one_shared_child_matches = True
                            break

                    if intersectifmultiple == False and at_least_one_shared_child_matches == True:
                        break

                    # we're here if we did not find a match for achild
                    if strictelements and not bchildmatchfound:
                        raise UnificationException('Missing child for {} {}'.format(childtag,
                                                                                    counter))
                if not at_least_one_shared_child_matches:
                    raise UnificationException('Empty intersection for {}'.format(childtag))

            elif required and not at_least_one_shared_child_matches:
                raise UnificationException('Missing match for {} {} {}'.format(childtag,
                                                                               achildcount,
                                                                               bchildcount))
        except UnificationException as e:
            logging.info("Subelements incompatible for {}: {}".format(childtag, e.value))
            raise
        else:
            logging.info("Subelements compatible for {}".format(childtag))

    def unify_boolean_subelement(self, ael, bel, abel, childns, childtag,
                                 required=True, strictelements=True, strictatts=True):
        return self.unify_simple_subelement(ael, bel, abel, childns, childtag,
                                            required=required,
                                            strictelements=strictelements,
                                            strictatts=strictatts,
                                            boolean=True)

    def unify_complex_subelement(self,
                                 acpp, bcpp, idtuple,
                                 ael, bel, abel, childns, childtag,
                                 handler,
                                 direction=None):
        logging.info("Unifying subelement {} for {}".format(childtag, ael.tag))
        try:
            aelements = ael.xpath('child::{}:{}'.format(childns, childtag),
                                namespaces=self.NSMAP)
            belements = bel.xpath('child::{}:{}'.format(childns, childtag),
                                namespaces=self.NSMAP)
            aelementcount = len(aelements)
            belementcount = len(belements)

            #if required and aelementcount == 0 and belementcount == 0:
            #    raise UnificationException('Missing child(ren) {}'.format(childtag))
            if aelementcount != belementcount:
                raise UnificationException('Mismatch in count for child(ren) {}'.format(childtag))
            elif aelementcount == 1 and belementcount == 1:
                logging.info('Creating {} element, invoking {}'.format(childtag, handler.func_name))
                abchild = lxml.etree.SubElement(abel,ns(self.NSMAP[childns], childtag),
                                                nsmap=self.NSMAP)
                handler(acpp, bcpp, idtuple, aelements[0], belements[0], abchild, direction)
                unify_atts(aelements[0], belements[0],abchild, strictatts=False)
            elif aelementcount == belementcount == 0:
                logging.info('Element {} not present'.format(childtag))
            else:
                logging.error('Help .... {} {}'.format(aelementcount,belementcount))
        except UnificationException as e:
            raise
        else:
            logging.info("Subelements compatible for {}".format(childtag))

    def cppaid(self, acppid, acid, bcppid, bcid):
        if (acppid, acid, bcppid, bcid) in self.shortened:
            return self.shortened[acppid, acid, bcppid, bcid]
        else:
            m = hashlib.sha224()
            m.update('{}_{}_{}_{}'.format(acppid,acid, bcppid, bcid))
            longvalue = '_'+base64.b32encode(m.digest())
            for i in range(5, 50):
                short = str(longvalue)[:i]
                if short not in self.collisions:
                    self.shortened[acppid, acid, bcppid, bcid] = short
                    self.collisions[short] = (acppid, acid, bcppid, bcid)
                    return short
                else:
                    logging.error('Collision {} for {} {} {} {}'.format(short,
                                                                        acppid,
                                                                        acid,
                                                                        bcppid,
                                                                        bcid))
                    (a, b, c, d) = self.collisions[short]
                    logging.error('Previous value for {} was {} {} {} {}'.format(short,
                                                                          a,
                                                                          b,
                                                                          c,
                                                                          d))
    def inline_channel_features(self, cpp):
        for feature_att in [ 'securityBinding',
                             'reliableMessagingBinding',
                             'errorHandling',
                             'receiptHandling',
                             'addressing']:

            for element in cpp.xpath('//node()[@{}]'.format(feature_att),
                                     namespaces= self.NSMAP):
                logging.info(element)
                binding_element = element.tag
                binding_id = element.get(feature_att)
                logging.info('Inlining feature with id {}'.format(binding_id))
                referenced_node = cpp.xpath('//node()[@id="{}"]'.format(binding_id ),
                                            namespaces= self.NSMAP)[0]
                copied_node = deepcopy(referenced_node)
                del element.attrib[feature_att]
                del copied_node.attrib['id']
                element.append(copied_node)
                logging.info('Inlined {} with id {}'.format(binding_element,
                                                            binding_id))

def cpp_level_acl_check(acpp, bcpp):
    a_allowed_party_list_id = acpp.get('allowed')
    b_allowed_party_list_id = bcpp.get('allowed')
    a_denied_party_list_id = acpp.get('denied')
    b_denied_party_list_id = bcpp.get('denied')
    acl_check(a_allowed_party_list_id, a_denied_party_list_id, acpp,
              b_allowed_party_list_id, b_denied_party_list_id, bcpp)

def service_specification_acl_check(a_service_spec, acpp,
                                    b_service_spec, bcpp):
    a_allowed_party_list_id = acpp.get('allowed')
    b_allowed_party_list_id = bcpp.get('allowed')
    a_denied_party_list_id = acpp.get('denied')
    b_denied_party_list_id = bcpp.get('denied')
    acl_check(a_allowed_party_list_id, a_denied_party_list_id, acpp,
              b_allowed_party_list_id, b_denied_party_list_id, bcpp)


def service_binding_acl_check(a_servicebinding, acpp, b_servicebinding, bcpp):
    logging.info('Checking ACLs for {}, {}'.format(
        a_servicebinding.xpath(
            'descendant::cppa:Description/text()',
            namespaces=_NSMAP
        ),
        b_servicebinding.xpath(
            'descendant::cppa:Description/text()',
            namespaces=_NSMAP
        ))
    )
    a_allowed_party_list_id = a_servicebinding.get('allowed')
    b_allowed_party_list_id = b_servicebinding.get('allowed')
    a_denied_party_list_id = a_servicebinding.get('denied')
    b_denied_party_list_id = b_servicebinding.get('denied')
    acl_check(a_allowed_party_list_id, a_denied_party_list_id, acpp,
              b_allowed_party_list_id, b_denied_party_list_id, bcpp)

def action_binding_acl_check(a_actionbinding, acpp,
                             b_actionbinding, bcpp):
    a_allowed_party_list_id = a_actionbinding.get('allowed')
    b_allowed_party_list_id = b_actionbinding.get('allowed')
    a_denied_party_list_id = a_actionbinding.get('denied')
    b_denied_party_list_id = b_actionbinding.get('denied')
    acl_check(a_allowed_party_list_id, a_denied_party_list_id, acpp,
              b_allowed_party_list_id, b_denied_party_list_id, bcpp)

def acl_check(a_allowed_party_list_id, a_denied_party_list_id, acpp,
              b_allowed_party_list_id, b_denied_party_list_id, bcpp):
    a_parties = deferenced_party_ids(acpp)
    b_parties = deferenced_party_ids(bcpp)
    if a_allowed_party_list_id == None:
        if b_allowed_party_list_id == None:
            pass
        else:
            b_allowed_parties = lookup_party_identifiers(bcpp,
                                                         b_allowed_party_list_id, [])
            acl_allow_match(b_allowed_parties, a_parties)
    else:
        a_allowed_parties = lookup_party_identifiers(acpp,
                                                     a_allowed_party_list_id, [])
        acl_allow_match(a_allowed_parties, b_parties)
        if b_allowed_party_list_id == None:
            pass
        else:
            b_allowed_parties = lookup_party_identifiers(bcpp,
                                                         b_allowed_party_list_id)
            acl_allow_match(b_allowed_parties, a_parties)

    if a_denied_party_list_id == None:
        if b_denied_party_list_id == None:
            pass
        else:
            b_denied_parties = lookup_party_identifiers(bcpp,
                                                        b_denied_party_list_id, [])
            acl_deny_match(b_denied_parties, a_parties)
    else:
        a_denied_parties = lookup_party_identifiers(acpp,
                                                    a_denied_party_list_id, [])
        b_parties = deferenced_party_ids(bcpp)
        acl_deny_match(a_denied_parties, b_parties)

        if b_denied_party_list_id == None:
            pass
        else:
            b_denied_parties = lookup_party_identifiers(bcpp,
                                                        b_denied_party_list_id)
            a_parties = deferenced_party_ids(acpp)
            acl_deny_match(b_denied_parties, a_parties)



def lookup_party_identifiers(cpp, id, parties=[]):
    party_id_list =  cpp.xpath('child::cppa:PartyIdList[@id="{}"]'.format(id),
                               namespaces=_NSMAP)[0]
    logging.debug('Found list with id {}'.format(id))
    for party_id in party_id_list.xpath('child::cppa:PartyId',
                                        namespaces=_NSMAP):
        pid = party_id.text
        pidtype = party_id.get('type')
        if (pid, pidtype) not in party_id_list:
            parties.append((pid,pidtype))
    for listref in party_id_list.xpath('child::cppa:PartyIdListRef/@href',
                                        namespaces=_NSMAP):
        parties = lookup_party_identifiers(cpp, listref, parties)
    return parties

def deferenced_party_ids(cpp):
    parties = []
    for party_id in cpp.xpath('descendant::cppa:PartyId',
                                        namespaces=_NSMAP):
        pid = party_id.text
        pidtype = party_id.get('type')
        if (pid, pidtype) not in parties:
            parties.append((pid,pidtype))
    return parties

def acl_allow_match(allowed_party_ids, party_ids):
    for (pid, ptype) in party_ids:
        if (pid, ptype) not in allowed_party_ids:
            raise UnificationException('{}, {} not in allowed list {}'.format(pid,
                                                                              ptype,
                                                                              allowed_party_ids))
        else:
            logging.debug('{}, {} found in allowed party list'.format(pid,
                                                                      ptype))

def acl_deny_match(denied_party_ids, party_ids):
    for (pid, ptype) in party_ids:
        if (pid, ptype) in denied_party_ids:
            raise UnificationException('{}, {} in denied list {}'.format(pid,
                                                                         ptype,
                                                                         denied_party_ids))
        else:
            logging.debug('{}, {} not in denied party list'.format(pid,
                                                                   ptype))



def check_x509_data_content(anchorid, rootcert, anchor_certid, cpp):
    anchor_cert = cpp.xpath('descendant::cppa:Certificate[@id="{}"]'.format(anchor_certid),
                            namespaces=_NSMAP)[0]
    anchor_cert_data = anchor_cert.xpath('descendant::ds:X509Certificate/text()',
                                         namespaces=_NSMAP)[0]
    anchor_cert_data = remove_all_whitespace(anchor_cert_data)
    logging.debug('Comparing against {} {} ... {} (len: {})'.format(anchor_certid,
                                                                    anchor_cert_data[0:6],
                                                                    anchor_cert_data[-6:],
                                                                    len(anchor_cert_data)))
    if str(rootcert) == str(anchor_cert_data):
        logging.info('Referenced X509Certificate found in anchor {} cert {}'.format(anchorid,
                                                                                    anchor_certid))
        return True
    else:
        return False

def unify_boolean_or_text(el1, el2, boolean):
    if boolean:
        return unify_boolean(el1, el2)
    else:
        return unify_text(el1, el2)

def unify_text(e1, e2):
    if e1.text == e2.text:
        return e1.text
    else:
        raise UnificationException('{}: {} vs {}'.format(e1.tag, e1.text, e2.text))

def unify_boolean(e1, e2):
    if (e1.text == 'true' or e1.text == 1) and (e2.text == 'true' or e1.text == 1):
        return 'true'
    elif (e1.text == 'false' or e1.text == 0) and (e2.text == 'false' or e1.text == 0):
        return 'false'
    else:
        raise UnificationException('Boolean {}: {} vs {}'.format(e1.tag, e1.text, e2.text))

def unify_atts(ael, bel, abel, strictatts=True, atts_to_match = None):
    for (aside, bside) in [(ael, bel), (bel, ael)]:
            for att in aside.attrib:
                if att != 'id':
                    if atts_to_match != None and att in atts_to_match:
                        if aside.attrib[att] == bside.attrib[att]:
                            abel.set(att, aside.attrib[att])
                        else:
                            raise UnificationException('Attribute {} value mismatch: {} vs {}'.format(att,
                                                                                                      aside.attrib[att],
                                                                                                      bside.attrib[att]))
                    elif atts_to_match == None  and att in bside.attrib:
                        if aside.attrib[att] == bside.attrib[att]:
                            abel.set(att, aside.attrib[att])
                        else:
                            raise UnificationException('Attribute {} value mismatch: {} vs {}'.format(att,
                                                                                                      aside.attrib[att],
                                                                                                      bside.attrib[att]))
                    elif strictatts:
                        # @@@ not covered yet
                        raise UnificationException('Attribute {} missing value in one of the inputs'.format(att))
                    else:
                        abel.set(att, aside.attrib[att])

def copy_atts(source, target):
    for att in source.attrib:
        target.set(att, source.get(att))

def unify_att(e1, e2, att):
    if not e1.attrib[att] == e2.attrib[att]:
        raise UnificationException('{}/@{}: {} vs {}'.format(e1.tag,
                                                             att,
                                                             e1.attrib[att],
                                                             e2.attrib[att]))
    else:
        return e1.attrib[att]

def unify_and_set_att(el1, el2, el3, att):
    if el1.get(att) == el2.get(att):
        if el1.get(att) != None:
            el3.set(att, el1.get(att))
    else:
        raise UnificationException('{}/@{}: {} vs {}'.format(el1.tag,
                                                             att,
                                                             el1.get(att),
                                                             el2.get(att)))

def unify_cardinality(aelement, belement, abelement, context=''):
    logging.info('Cardinality check for {}'.format(context))

    for att in ['minOccurs', 'maxOccurs']:
        amin = aelement.get(att)
        bmin = belement.get(att)
        if amin == bmin:
            if amin is None:
                pass
            else:
                abelement.set(att, amin)
        if amin != bmin:
            raise UnificationException('Incompatible {} cardinality in {}: {} vs {}'.format(att,
                                                                                            context,
                                                                                            amin,
                                                                                            bmin))
        elif amin is not None:
            abelement.set(att, amin)

def reverse(direction):
    if direction == 'send':
        return 'receive'
    else:
        return 'send'

def cppa(el):
    return '{{{}}}{}'.format(_NSMAP['cppa'],el)

def xml(el):
    return '{{{}}}{}'.format(_NSMAP['xml'],el)

def ns(ns,el):
    return '{{{}}}{}'.format(ns,el)

def get_description_value_if_present(el):
    descriptions = el.xpath('child::cppa:Description',
                     namespaces=_NSMAP)
    if len(descriptions)>0:
        return descriptions[0].text
    else:
        return '-'

def create_username(acppid, aelid, bcppid, belid, len=15):
    m = hashlib.sha224()
    m.update('{}_{}_{}_{}'.format(acppid, aelid, bcppid, belid))
    longvalue = base64.b64encode(m.digest())
    return str(longvalue)[:len]

def create_random_password(len=20):
    return str(uuid.uuid4())[:len]

def remove_all_whitespace(inputstring):
    pattern = re.compile(r'\s+')
    return re.sub(pattern, '', inputstring)

def xsd_boolean(value):
    if value == '1':
        return True
    elif value == 'true':
        return True
    elif value == '0':
        return False
    elif value == 'false':
        return False
    else:
        return None

