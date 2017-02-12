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
by all configuration processors
"""


class ProcessorInterface():
    
    """
    /**
     * Process the whole Config structure and recursively parse all its values.
     *
     * @param  Config $value
     * @return Config
     */
    """
    def process(self, value):
        raise RuntimeException("ProcessorInterface: process not implemented in child class")
    
    """
    /**
     * Process a single value
     *
     * @param  mixed $value
     * @return mixed
     */
    """
    def processValue(self, value):
        raise RuntimeException("ProcessorInterface: processValue not implemented in child class")
