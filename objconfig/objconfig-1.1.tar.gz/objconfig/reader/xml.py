"""
This is a port of zend-config to Python

Some idioms of PHP are still employed, but where possible I have Pythonized it

Author: Asher Wolfstein (http://wunk.me/)
Package Homepage: http://wunk.me/programming-projects/objconfig-python/
GitHub: http://github.com/asherwunk/objconfig for the source repository

Following is the header as given in zend-config:

/**
 * Zend Framework (http://framework.zend.com/)
 *
 * @link      http://github.com/zendframework/zf2 for the
 *            canonical source repository
 * @copyright Copyright (c) 2005-2015 Zend Technologies USA Inc.
 *            (http://www.zend.com)
 * @license   http://framework.zend.com/license/new-bsd New BSD License
 */
"""

from objconfig.reader import ReaderInterface
from objconfig.exception import RuntimeException
import xml.etree.ElementTree as ElementTree
import xml.etree.ElementInclude as ElementInclude
import os

"""
Following is the class documentation as given in zend-config:

/**
 * XML config reader.
 */
"""


class Xml(ReaderInterface):
    
    def loader(self, href, parse, encoding=None):
        if href[0] != '/':
            href = os.path.join(self.directory, href)
        if not os.path.isfile(href) or not os.access(href, os.R_OK):
            raise RuntimeException("Xml: File %s Doesn't Exist or Not Readable (xi)" % href)
        
        file = open(href)
        if parse == "xml":
            data = ElementTree.parse(file).getroot()
        else:
            data = file.read()
            if encoding:
                data = data.decode(encoding)
        file.close()
        return data
    
    def __init__(self):
        """
        Actually ElementTree root element
        
        /**
         * XML Reader instance.
         *
         * @var XMLReader
         */
        """
        self.root = None
        
        """
        /**
         * Directory of the JSON file
         *
         * @var string
         */
        """
        self.directory = ''
    
    """
    /**
     * fromFile(): defined by Reader interface.
     *
     * @see    ReaderInterface::fromFile()
     * @param  string $filename
     * @return array
     * @throws Exception\RuntimeException
     */
    """
    def fromFile(self, filename):
        if not os.path.isfile(filename) and not os.access(filename, os.R_OK):
            raise RuntimeException("Xml: File %s Doesn't Exist or Not Readable" % filename)
        
        self.directory = os.path.dirname(filename.rstrip(os.sep)) or '.'
        
        try:
            xmlcontent = ''
            with open(filename, "r") as file:
                for line in file:
                    if "@include" in line:
                        include = line.split(":")[1].strip()
                        with open(os.path.join(self.directory, include), "r") as includedfile:
                            for includedline in includedfile:
                                xmlcontent += includedline
                    else:
                        xmlcontent += line
            
            self.root = ElementTree.fromstring(xmlcontent)
            ElementInclude.include(self.root, self.loader)
        except ElementTree.ParseError as e:
            raise RuntimeException("Xml: Error Reading XML file \"%s\": %s" % (filename, e))
        
        return self.process(self.root)
    
    """
    /**
     * fromString(): defined by Reader interface.
     *
     * @param  string $string
     * @return array|bool
     * @throws Exception\RuntimeException
     */
    """
    def fromString(self, string):
        if not string:
            return {}
        
        self.directory = None
        
        if "@include" in string:
            raise RuntimeException("Xml: Cannot Process @include When Reading From String")
        
        try:
            self.root = ElementTree.fromstring(string)
        except ElementTree.ParseError as e:
            raise RuntimeException("Xml: Error Reading XML string: %s" % e)
        
        return self.process(self.root)
    
    """
    /**
     * Process the next inner element.
     *
     * @return mixed
     */
    """
    def process(self, elem):
        ret = {}
        
        for child in elem:
            if not child.getchildren():
                if child.attrib and ("value" in child.attrib):
                    ret[child.tag] = child.attrib["value"]
                else:
                    ret[child.tag] = child.text
            else:
                ret[child.tag] = self.process(child)
        
        return ret
