#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 3 févr. 2016

@author: Adrien
'''
from lxml import etree
from dateutil import parser
from django.utils.timezone import utc

NODE_TYPES={
    'BOOL':'boolean',
    'DATETIME':'datetime',
    'ENUM':'enum',
}

class Plcm(object):

    root_element = None
    target_namespace = None
    imported_namespaces = None
    xml_source = None
    content_type = None
    xml_source = {}
    
    def xml_build_root(self, build_nsmap=True, existing_nsmap=None):
        #print "build_root %s" % self.root_element
        NSMAP = self.xml_populate_nsmap(existing_nsmap) if build_nsmap else {}
        #print "+++ build_root %s;%s;%s" %(self.target_namespace,self.root_element, NSMAP)
        root = etree.Element("{%s}%s" % ( self.target_namespace,self.root_element),nsmap=NSMAP)
        return root
    
    def xml_build_content(self, xml_root, nsmap=None):
        content = etree.Element(xml_root)
        return content
    
    def xml_build(self, build_nsmap=True, nsmap=None):
        root = self.xml_build_root(build_nsmap=build_nsmap,existing_nsmap=nsmap)
        content = self.xml_build_content(root, nsmap=nsmap)
        #print "nsmap %s %d" % (root,len(nsmap) if nsmap is not None else 0)
        return root
    
    def xml_tostring(self, build_nsmap=True):
        '''Build XML representation of instance'''
        #print etree.tostring(self.xml_build(build_nsmap),pretty_print=True)
        return etree.tostring(self.xml_build(build_nsmap),pretty_print=True)
        
    def get_content_type(self):
        return self.content_type
    
    def xml_populate_nsmap(self, existing_nsmap=None):
        #print "pop nsmap %s" % self.root_element
        '''Complete the Nsmap passed with instance imported namespaces'''
        if existing_nsmap != None:
            NSMAP = existing_nsmap
            if self.imported_namespaces:
                for ns in self.imported_namespaces:
                    if ns not in existing_nsmap.keys():
                        NSMAP["%s%d"%('ns',len(NSMAP)-1)] = ns
                        #print ns + " added! %s" % self.root_element
        else:
            NSMAP = {None:self.target_namespace}
            if self.imported_namespaces:
                for i,ns in enumerate(self.imported_namespaces):
                    NSMAP["%s%d"%('ns',i)] = ns
        return NSMAP
    
    def xml_build_from_properties(self, xml_root, nsmap=None):
        ''' Generate xml from object's instance '''
        #pprint(nsmap)
        for prop in self.element_properties:
            property_name = prop
            #print prop
            property_conf = self.element_properties[property_name]
            property_name = property_conf['prop']
            if property_name in self.__dict__ and self.__dict__[property_name] is not None:
                element = etree.SubElement(xml_root,'{%s}%s' %(self.target_namespace, property_conf['tag']))
                if 'type' in property_conf:
                    if property_conf['type'] == NODE_TYPES['BOOL']:
                        value = 'true' if self.__dict__[property_name] else 'false'
                        
                    elif property_conf['type'] == NODE_TYPES['DATETIME']:
                        date_value = self.__dict__[property_name]
                        #Without timezone RPRM goes to status error 500 on recur_time
                        if date_value.tzinfo == None:
                            date_value = date_value.replace(tzinfo=utc)
                        value = date_value.isoformat()
                        
                    elif property_conf['type'] == NODE_TYPES['ENUM']:
                        enum = property_conf['values']
                        if self.__dict__[property_name] in enum:
                            value = enum[self.__dict__[property_name]]
                        else:
                            print "[prpp][err]invalid enum value ", self.__dict__[property_name]
                    
                    elif 'class' in property_conf:
                        xml_root.remove(element)
                        if 'list' in property_conf and property_conf['list'] == True:
                            for item in self.__dict__[property_name]:
                                xml_root.append(item.xml_build(build_nsmap=False, nsmap=nsmap))
                                #print item
                        else:
                            xml_elt = self.__dict__[property_name].xml_build(build_nsmap=True, nsmap=nsmap)
                            if len(xml_elt.getchildren())>0:
                                xml_root.append(xml_elt)
                            #print "*****%s/%s*****" %(property_name,self.__dict__[property_name].xml_build(build_nsmap=True, nsmap=nsmap).getchildren())
                        value = None
                    
                    else:
                        print "[prpp][err]type invalid", property_conf['type']
                else:
                    value = self.__dict__[property_name]
                #print "---->",value
                if value != None:
                    element.text = unicode(value)
            else:
                if 'mandatory' in property_conf:
                    if property_conf['mandatory']:
                        print "[prpp][war]property is mandatory and missing!", property_name
        return xml_root
    
    
    def xml_parse(self, xml_element):
        '''Populate current instance properties using xml'''
        #print "[prpp]xml_parse %s" % xml_element
        node_tag = xml_element.tag.split('}',1)[1]
        #if node_tag == self.root_element:
        for node in xml_element:
            self.xml_parse_node(node)
        #else:
            #raise Exception("Xml element to parse:", xml_element.tag," does not equals attended root element:", self.root_element)
        
        print("[prpp]parsing ok %s" % self)
        return self
    
    def xml_parse_node(self,node):
        #print "parsing ",self.root_element,"#",node.tag, ":",node.text
        node_tag = node.tag.split('}',1)[1]
        node_ns = node.tag[1:len(node.tag)].split('}',1)[0]
        
        if node_tag in self.element_properties:
            if node_ns == self.target_namespace or node_ns in self.imported_namespaces:
                property_conf = self.element_properties[node_tag]
                if 'type' in property_conf:
                    if property_conf['type'] == NODE_TYPES['BOOL']:
                        value = True if node.text in ('true','1') else False
                    elif property_conf['type'] == NODE_TYPES['DATETIME']:
                        value = parser.parse(node.text)
                    elif property_conf['type'] == NODE_TYPES['ENUM']:
                        values = property_conf['values']
                        if node.text in values:
                            value = values[node.text]
                            #print "!!! %s=%s" %(node_tag,value)
                        else:
                            print "[prpp][err]unknown value for enum type ", node.text, node_tag
                            value = node.text
                            
                    elif property_conf['type'] in self.imported_namespaces:
                        if 'list' in property_conf and property_conf['list']==True:
                            if property_conf['prop'] not in self.__dict__:
                                value = []
                            else:
                                value = self.__dict__[property_conf['prop']]
                            value.append(property_conf['class']().xml_parse(node))
                        else:
                            value = property_conf['class']().xml_parse(node)
                            #print value
                        #pprint(value)
                    else:
                        print "[prpp][err]unknown type :",property_conf['type']
                        value = node.text
                else:
                    value = node.text
                    
                self.__dict__[property_conf['prop']] = value
                #print property_conf['prop'],'=',value
            else:
                print "[prpp][err] %s not known" % node_ns
            #pprint(self.__dict__)

        if node_tag == 'link':
            if not 'links' in self.__dict__:
                self.__dict__['links']=[]
            self.__dict__['links'].append(node.attrib)
        
        #self.xml_source[property] = node.text


'''
    def xml_parse_link(self,node_link):
        print "parsing link ",node_link
        pprint(node_link.attrib)
        link = {
            'href':node_link.attrib['href'] if 'href' in node_link.attrib else None,
            'base':node_link.attrib['base'] if 'base' in node_link.attrib else None,
            'lang':node_link.attrib['lang'] if 'lang' in node_link.attrib else None,
            'ref':node_link.attrib['ref'] if 'ref' in node_link.attrib else None,
            'type':node_link.attrib['type'] if 'type' in node_link.attrib else None,
            'hreflang':node_link.attrib['hreflang'] if 'hreflang' in node_link.attrib else None,
            'title':node_link.attrib['title'] if 'title' in node_link.attrib else None,
            'length':node_link.attrib['length'] if 'length' in node_link.attrib else None,
            
                }
        return link
'''
            
class PlcmString(Plcm):
    root_element = "plcm-string"
    target_namespace = "urn:com:polycom:api:rest:plcm-string"
    imported_namespaces = [
        'urn:com:polycom:api:rest:plcm-objects',
    ]
    element_properties={
        'value':{'prop':'value','tag':'value'},
    }
        
class PlcmStringList(Plcm):
    root_element = "plcm-string-list"
    target_namespace = "urn:com:polycom:api:rest:plcm-string-list"
    imported_namespaces = [
        'urn:com:polycom:api:rest:plcm-string',
        'urn:com:polycom:api:rest:plcm-objects',
    ]
    element_properties={
        'plcm-string':{'prop':'plcm_strings','tag':'plcm-string','type':'urn:com:polycom:api:rest:plcm-string','class':PlcmString,'list':True},
    }