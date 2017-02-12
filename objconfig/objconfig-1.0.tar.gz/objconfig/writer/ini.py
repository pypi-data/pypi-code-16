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

"""
Following is the class documentation as given in zend-config:

"""


class Ini(AbstractWriter):
    
    def __init__(self, nestSeparator='.', renderWithoutSections=False):
        """
        /**
         * Separator for nesting levels of configuration data identifiers.
         *
         * @var string
         */
        """
        self.nestSeparator = nestSeparator
        
        """
        /**
         * If true the INI string is rendered in the global namespace without
         * sections.
         *
         * @var bool
         */
        """
        self.renderWithoutSections = renderWithoutSections
    
    """
    /**
     * Set nest separator.
     *
     * @param  string $separator
     * @return self
     */
    """
    def setNestSeparator(self, separator):
        self.nestSeparator = separator
        return self
    
    """
    /**
     * Get nest separator.
     *
     * @return string
     */
    """
    def getNestSeparator(self):
        return self.nestSeparator
    
    """
    /**
     * Set if rendering should occur without sections or not.
     *
     * If set to true, the INI file is rendered without sections completely
     * into the global namespace of the INI file.
     *
     * @param  bool $withoutSections
     * @return Ini
     */
    """
    def setRenderWithoutSectionsFlags(self, withoutSections):
        self.renderWithoutSections = withoutSections
        return self
    
    """
    /**
     * Return whether the writer should render without sections.
     *
     * @return bool
     */
    """
    def shouldRenderWithoutSections(self):
        return self.renderWithoutSections
    
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
        iniContents = ''
        if self.shouldRenderWithoutSections():
            iniContents = "[DEFAULT]\n" + self.addBranch(config)
        else:
            config = self.sortRootElements(config)
            if not config["DEFAULT"]:
                del config["DEFAULT"]
            for sectionName, data in config.items():
                if not isinstance(data, dict):
                    iniContents += sectionName + " = " + self.prepareValue(data) + "\n"
                else:
                    iniContents += "[" + sectionName + "]\n" + self.addBranch(data) + "\n"
        return iniContents
    
    """
    /**
     * Add a branch to an INI string recursively.
     *
     * @param  array $config
     * @param  array $parents
     * @return string
     */
    """
    def addBranch(self, config, parents=None):
        if parents is None:
            parents = []
        iniContents = ''
        for key, value in config.items():
            group = parents + [key]
            if isinstance(value, dict):
                iniContents += self.addBranch(value, group)
            else:
                iniContents += self.nestSeparator.join(group) + " = " + self.prepareValue(value) + "\n"
        return iniContents
    
    """
    NOTE:
        Just converts to string (minus double-quotes)
    
    /**
     * Prepare a value for INI.
     *
     * @param  mixed $value
     * @return string
     * @throws Exception\RuntimeException
     */
    """
    def prepareValue(self, value):
        if '"' in str(value):
            raise RuntimeException("Ini: Value Cannot Contain Double Quotes")
        else:
            return str(value)
    
    """
    NOTE:
        Default section replaces empty section, as Ini reader won't read wihtout sections
    
    /**
     * Root elements that are not assigned to any section needs to be on the
     * top of config.
     *
     * @param  array $config
     * @return array
     */
    """
    def sortRootElements(self, config):
        ret = {"DEFAULT": {}}
        for key, value in config.items():
            if not isinstance(value, dict):
                ret["DEFAULT"].update(key, value)
            else:
                ret[key] = value
        return ret
