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

from objconfig.writer import AbstractWriter
from objconfig.exception import InvalidArgumentException
from objconfig.exception import RuntimeException
import inspect
import xml.etree.ElementTree as ElementTree

"""
Following is the class documentation as given in zend-config:

"""


class Xml(AbstractWriter):
    
    def __init__(self):
        self.tree = None
    
    """
    /**
     * toFile(): defined by Writer interface.
     *
     * @see    WriterInterface::toFile()
     * @param  string  $filename
     * @param  mixed   $config
     * @param  bool $exclusiveLock
     * @return void
     * @throws Exception\InvalidArgumentException
     * @throws Exception\RuntimeException
     */
    """
    def toFile(self, filename, config):
        if not ('toArray' in dir(config) and inspect.ismethod(config.toArray)) and not isinstance(config, dict):
            raise InvalidArgumentException("AbstractWriter: toFile() expects a dictionary or implementing toArray")
        
        if not filename:
            raise InvalidArgumentException("AbstractWriter: No Filename Specified")
        
        # I don't think python has the idea of an exclusive lock? see PHP implementation
        
        self.processConfig(config)
        
        try:
            self.tree.write(filename, xml_declaration=True)
        except Exception as e:
            raise RuntimeException("AbstractWriter: Error Writing to \"%s\": %s" % (filename, e))
    
    """
    /**
     * fromString(): defined by Reader interface.
     *
     * @param  string $string
     * @return array|bool
     * @throws Exception\RuntimeException
     */
    """
    def toString(self, config):
        if not ('toArray' in dir(config) and inspect.ismethod(config.toArray)) and not isinstance(config, dict):
            raise InvalidArgumentException("AbstractWriter: toString() expects a dictionary or implementing toArray")
        
        self.processConfig(config)
        
        return ElementTree.tostring(self.tree.getroot()).decode()
    
    """
    /**
     * processConfig(): defined by AbstractWriter.
     *
     * @param  array $config
     * @return string
     */
    """
    def processConfig(self, config):
        config = config.toArray() if 'toArray' in dir(config) and inspect.ismethod(config.toArray) else config
        root = ElementTree.Element("zend-config")
        for sectionName, data in config.items():
            element = ElementTree.Element(sectionName)
            if not isinstance(data, dict):
                element.text = data
            else:
                self.addBranch(sectionName, data, element)
            root.append(element)
        
        self.tree = ElementTree.ElementTree(root)
    
    """
    /**
     * Add a branch to an XML object recursively.
     *
     * @param  string    $branchName
     * @param  array     $config
     * @param  XMLWriter $writer
     * @return void
     * @throws Exception\RuntimeException
     */
    """
    def addBranch(self, branchName, config, root):
        for key, value in config.items():
            element = ElementTree.Element(key)
            if not isinstance(value, dict):
                element.text = value
            else:
                self.addBranch(key, value, element)
            root.append(element)
