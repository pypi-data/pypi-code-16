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

from objconfig.exception import InvalidArgumentException
from objconfig.processor import ProcessorInterface
from objconfig import Config
import inspect

"""
Following is the class documentation as given in zend-config:

"""


class Token(ProcessorInterface):
    
    """
    /**
     * Token Processor walks through a Config structure and replaces all
     * occurrences of tokens with supplied values.
     *
     * @param  array|Config|Traversable   $tokens  Associative array of TOKEN => value
     *                                             to replace it with
     * @param    string $prefix
     * @param    string $suffix
     * @return   Token
     */
    """
    def __init__(self, tokens=None, prefix='', suffix=''):
        """
        /**
         * Token prefix.
         *
         * @var string
         */
        """
        self.setPrefix(prefix)
        
        """
        /**
         * Token suffix.
         *
         * @var string
         */
        """
        self.setSuffix(suffix)
        
        """
        /**
         * The registry of tokens
         *
         * @var array
         */
        """
        self.setTokens(tokens)
        
        """
        /**
         * Replacement map
         *
         * @var array
         */
        """
        self.map = None
    
    """
    /**
     * @param  string $prefix
     * @return Token
     */
    """
    def setPrefix(self, prefix):
        self.map = None
        self.prefix = prefix
        return self
    
    """
    /**
     * @return string
     */
    """
    def getPrefix(self):
        return self.prefix
    
    """
    /**
     * @param  string $suffix
     * @return Token
     */
    """
    def setSuffix(self, suffix):
        self.map = None
        self.suffix = suffix
        return self
    
    """
    /**
     * @return string
     */
    """
    def getSuffix(self):
        return self.suffix
    
    """
    /**
     * Set token registry.
     *
     * @param  array|Config|Traversable  $tokens  Associative array of TOKEN => value
     *                                            to replace it with
     * @return Token
     * @throws Exception\InvalidArgumentException
     */
    """
    def setTokens(self, tokens):
        if tokens is not None:
            self.tokens = tokens.toArray() if 'toArray' in dir(tokens) and inspect.ismethod(tokens.toArray) else tokens
        else:
            self.tokens = {}
        
        if not isinstance(self.tokens, dict):
            self.tokens = {}
            try:
                for key, val in tokens.items():
                    self.tokens[key] = val
            except Exception:
                raise InvalidArgumentException("Token: Cannot Use %s As Token Registry" % type(tokens))
    
        self.map = None
        return self
    
    """
    /**
     * Get current token registry.
     *
     * @return array
     */
    """
    def getTokens(self):
        return self.tokens
    
    """
    /**
     * Add new token.
     *
     * @param  string $token
     * @param  mixed $value
     * @return Token
     * @throws Exception\InvalidArgumentException
     */
    """
    def addToken(self, token, value):
        if not isinstance(str(token), str):
            raise InvalidArgumentException("Token: Cannot Use %s As Token Name" % type(token))
        
        self.tokens[str(token)] = value
        self.map = None
        return self
    
    """
    /**
     * Add new token.
     *
     * @param string $token
     * @param mixed $value
     * @return Token
     */
    """
    def setToken(self, token, value):
        return self.addToken(token, value)
    
    """
    /**
     * Build replacement map
     *
     * @return array
     */
    """
    def buildMap(self):
        if self.map is None:
            if not self.suffix and not self.prefix:
                self.map = self.tokens
            else:
                self.map = {}
                for token, value in self.tokens.items():
                    self.map[self.prefix + token + self.suffix] = value
            
            """
            foreach (array_keys($this->map) as $key) {
                if (empty($key)) {
                    unset($this->map[$key]);
                }
            }
            """   # -- ?
            
        return self.map
    
    """
    /**
     * Process
     *
     * @param  Config $config
     * @return Config
     * @throws Exception\InvalidArgumentException
     */
    """
    def process(self, config):
        return self.doProcess(config, self.buildMap())
    
    """
    /**
     * Process a single value
     *
     * @param $value
     * @return mixed
     */
    """
    def processValue(self, value):
        return self.doProcess(value, self.buildMap())
    
    """
    /**
     * Applies replacement map to the given value by modifying the value itself
     *
     * @param mixed $value
     * @param array $replacements
     *
     * @return mixed
     *
     * @throws Exception\InvalidArgumentException if the provided value is a read-only {@see Config}
     */
    """
    def doProcess(self, value, replacements):
        if isinstance(value, Config):
            if value.isReadOnly():
                raise InvalidArgumentException("Token: Cannot Process Config Because It Is Read-Only")
            ret = Config({}, True)
            for key, val in value:
                ret.__dict__[key] = self.doProcess(val, replacements)
            return ret
        elif isinstance(value, dict):
            for key, val in value.items():
                value[key] = self.doProcess(val, replacements)
            return value
        else:
            stringval = str(value)
            for fr, to in self.map.items():
                stringval = stringval.replace(fr, to)
            """
            if ($changedVal !== $stringVal) {
                return $changedVal;
            }
            """  # -- ?
            
            return stringval
