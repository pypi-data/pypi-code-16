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

from objconfig.exception import RuntimeException

"""
The following is an 'interface' (abstraction) to be implemented
by all configuration writers
"""


class WriterInterface():
    
    """
    /**
     * Write a config object to a file.
     *
     * @param  string  $filename
     * @param  mixed   $config
     * @param  bool $exclusiveLock
     * @return void
     */
    """
    def toFile(self, filename, config):
        raise RuntimeException("WriterInterface: toFile not implemented in child class")
    
    """
    /**
     * Write a config object to a string.
     *
     * @param  mixed $config
     * @return string
     */
    """
    def toString(self, config):
        raise RuntimeException("WriterInterface: toString not implemented in child class")
