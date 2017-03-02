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

from objconfig.writer import WriterInterface
from objconfig.exception import RuntimeException
from objconfig.exception import InvalidArgumentException
import inspect
import portalocker

"""
Following is the class documentation as given in zend-config:

"""


class AbstractWriter(WriterInterface):
    
    """
    CHANGELOG:
    objconfig v1.1: use portalocker to establish an exclusive lock if given
    
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
    def toFile(self, filename, config, exclusive=True):
        if not ('toArray' in dir(config) and inspect.ismethod(config.toArray)) and not isinstance(config, dict):
            raise InvalidArgumentException("AbstractWriter: toFile() expects a dictionary or implementing toArray")
        
        if not filename:
            raise InvalidArgumentException("AbstractWriter: No Filename Specified")
        
        try:
            with open(filename, "w") as file:
                if exclusive:
                    portalocker.lock(file, portalocker.LOCK_EX)
                file.write(self.toString(config))
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
        
        return self.processConfig(config)
    
    """
    /**
     * @param array $config
     * @return string
     */
    """
    def processConfig(self, config):
        raise RuntimeException("AbstractWriter: processConfig not implemented in child class")
