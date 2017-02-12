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
import json
import os

"""
Following is the class documentation as given in zend-config:

/**
 * JSON config reader.
 */
"""


class Json(ReaderInterface):
    
    def __init__(self):
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
        if not os.path.isfile(filename) or not os.access(filename, os.R_OK):
            raise RuntimeException("Json: File %s Doesn't Exist or Not Readable" % filename)
        
        self.directory = os.path.dirname(filename.rstrip(os.sep)) or '.'
        
        ret = {}
        
        try:
            jsoncontent = ''
            with open(filename, "r") as file:
                for line in file:
                    if "@include" in line:
                        include = line.split(":")[1].strip()[1:-1]
                        if include[0] != '/':
                            include = os.path.join(self.directory, include)
                        if (not os.path.isfile(os.path.join(self.directory, include))
                                or not os.access(os.path.join(self.directory, include), os.R_OK)):
                            raise RuntimeException("Json: File %s Doesn't Exist or Not Readable" % os.path.join(self.directory, include))
                        with open(include, "r") as includedfile:
                            for includedline in includedfile:
                                jsoncontent += includedline
                    else:
                        jsoncontent += line
            
            ret = json.loads(jsoncontent)
        except Exception as e:
            raise RuntimeException("Json: Error Reading JSON file \"%s\": %s" % (filename, e))
        
        if not isinstance(ret, dict):
            ret = {"DEFAULT": ret}
        
        return ret
    
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
        
        ret = {}
        
        if "@include" in string:
            raise RuntimeException("Json: Cannot Process @include When Reading From String")
        
        try:
            ret = json.loads(string)
        except Exception as e:
            raise RuntimeException("Json: Error Reading JSON string: %s" % e)
        
        if not isinstance(ret, dict):
            ret = {"DEFAULT": ret}
        
        return ret
