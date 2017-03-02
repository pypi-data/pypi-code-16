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
from objconfig.exception import RuntimeException
import inspect
import yaml

"""
Following is the class documentation as given in zend-config:

"""


class Yaml(AbstractWriter):
    
    """
    /**
     * processConfig(): defined by AbstractWriter.
     *
     * @param  array $config
     * @return string
     * @throws Exception\RuntimeException
     */
    """
    def processConfig(self, config):
        config = config.toArray() if 'toArray' in dir(config) and inspect.ismethod(config.toArray) else config
        ret = ''
        try:
            ret = yaml.dump(config, default_flow_style=False)
        except Exception as e:
            raise RuntimeException("Yaml: unable to process config: %s" % e)
        
        return ret
