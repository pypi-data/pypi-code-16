# coding:utf-8
'''
Created on 2016年11月5日

@author: shenlang
'''
from appium import webdriver
import time
import base64
from selenium.common.exceptions import TimeoutException
from appium.webdriver.common.touch_action import TouchAction
from unicodedata import normalize
from robot.libraries.BuiltIn import logger,BuiltIn
import ast

baseUrl = 'http://127.0.0.1'




def log(level, msg):
    if level == 'error':
        logger.error(msg, html=True)
    elif level == 'warn':
        logger.warn(msg, html=True)
    elif level == 'info':
        logger.info(msg, html=True)
    elif level == 'debug':
        logger.debug(msg, html=True)
    elif level == 'trace':
        logger.trace(msg, html=True)


class InvalidOperationException(Exception):
    pass

    
class AppiumClient:
    driver = None
    
    def __init__(self):
#         desired_caps = {}
#         desired_caps['platformName'] = platformName
#         desired_caps['platformVersion'] = platformVersion
#         desired_caps['deviceName'] = deviceName
#         desired_caps['appPackage'] = packageName
#         desired_caps['appActivity'] = acvitiyName
#         self.driver = webdriver.Remote(baseUrl + ':' + str(port)  + '/wd/hub', desired_caps)
#         self.driver.implicitly_wait(30)
        self.driverDict = {}
        self._bi = BuiltIn()
    
    
       
    def getDriver(self, port=0):
        if port:
            return self.driverDict[port]
        elif len(self.driverDict) == 1:
            return self.driverDict.values()[0]
        elif len(self.driverDict) > 1:
            return self.driver
        else:
            raise Exception('NO Available Driver')
    
    #导致会退出
#     def __del__(self):
#         if self.driver:
#             self.driver.quit()
    
    '''
    单位秒
    '''
    def implicitlyWait(self, time_to_wait=5):
        time_to_wait = int(time_to_wait)
        self.driver.implicitly_wait(time_to_wait)
    
    def backgroundApp(self, seconds):
        self.driver.background_app(seconds)
    
    def screenshot(self, filename):
        self.driver.save_screenshot(filename)
    
    
    def _element_clear_text_by_locator(self, by, locator, index=0):
        try:
            element = self._findElementWithBy(by, locator, index)
            element.clear()
        except:
            raise InvalidOperationException('clear element[%s] fail' %  locator)
    
    def _isstr(self, s):
        return isinstance(s, str)
    
    
    
    
    def clearText(self, by, locator, index=0):
        self._element_clear_text_by_locator(by, locator, index)
    
    def getPlatform(self):
        try:
            platform_name = self.driver.desired_capabilities['platformName']
        except Exception as e:
            raise e
        return platform_name.lower()

    def _is_platform(self, platform):
        platform_name = self._get_platform()
        return platform.lower() == platform_name

    def isIos(self):
        return self._is_platform('ios')

    def isAndroid(self):
        return self._is_platform('android')
    
    def clickAPoint(self, x=0, y=0, duration=100):
        """ Click on a point"""
        log('info',"Clicking on a point (%s,%s)." % (x,y))
        action = TouchAction(self.driver)
        try:
            action.press(x=float(x), y=float(y)).wait(float(duration)).release().perform()
        except:
            raise InvalidOperationException("Can't click on a point at (%s,%s)" % (x,y))
    
    def clickButton(self, index_or_name):
        """ Click button """
        _platform_class_dict = {'ios': 'UIAButton',
                                'android': 'android.widget.Button'}
        if self._is_support_platform(_platform_class_dict):
            class_name = self._get_class(_platform_class_dict)
            self.clickElementByClassName(class_name, index_or_name)
        else:
            raise InvalidOperationException('current platform[%s]' %  self._get_platform() + ' is not supported')
    
    def _get_class(self, platform_class_dict):
        return platform_class_dict.get(self._get_platform())

    def _is_support_platform(self, platform_class_dict):
        return platform_class_dict.has_key(self.getPlatform())
    

    
    def _find_element_by_class_name(self, class_name, index_or_name=None):
        if index_or_name:
            elements = self.driver.find_elements_by_class_name(class_name)
            if self._is_index(index_or_name):
                try:
                    index = int(index_or_name.split('=')[-1])
                    element = elements[index]
                except (IndexError, TypeError):
                    raise InvalidOperationException('Cannot find the element with index "%s"' % index_or_name)
            else:
                found = False
                for element in elements:
                    log('info',"'%s'." % element.text)
                    if element.text == index_or_name:
                        found = True
                        break
                if not found:
                    raise InvalidOperationException('Cannot find the element with name "%s"' % index_or_name)
        else:
            try:
                element =  self.driver.find_element_by_class_name(class_name)
            except Exception:
                raise InvalidOperationException('Cannot find the element with name "%s"' % class_name)
        return element
    
    def clickElementByClassName(self, class_name, index_or_name):
        element = self._find_element_by_class_name(class_name, index_or_name)
        log('info',"Clicking element '%s'." % element.text)
        try:
            element.click()
        except:
            raise InvalidOperationException('Cannot click the %s element "%s"' % (class_name, index_or_name))
    
    def _findElementWithBy(self, by, locator, index=0):
        
        element = None
        if by == 'id':
            if index:
                element = self.driver.find_elements_by_id(locator)[index]
            else:
                element = self.driver.find_element_by_id(locator)
        
        elif by == 'accessibilityId':
            if index:
                element = self.driver.find_elements_by_accessibility_id(locator)[index]
            else:
                element = self.driver.find_element_by_accessibility_id(locator)
        
        elif by == 'className':
            if index:
                element = self.driver.find_elements_by_class_name(locator)[index]
            else:
                element = self.driver.find_element_by_class_name(locator)
        
        elif by == 'xpath':
            if index:
                element = self.driver.find_elements_by_xpath(locator)[index]
            else:
                element = self.driver.find_element_by_xpath(locator)
        
        elif by == 'uiaString':
            platform = self.getPlatform()
            if platform == 'ios':
                if index:
                    element = self.driver.find_elements_by_android_uiautomator(locator)[index]
                else:
                    element = self.driver.find_element_by_android_uiautomator(locator)
            
            elif platform == 'android':
                if index:
                    element = self.driver.find_elements_by_ios_uiautomation(locator)[index]
                else:
                    element = self.driver.find_element_by_ios_uiautomation(locator) 
            
        
        elif by == 'predicateString':
            if index:
                element = self.driver.find_elements_by_ios_predicate(locator)[index]
            else:
                element = self.driver.find_element_by_ios_predicate(locator)
        
        elif by == 'css':
            if index:
                element = self.driver.find_elements_by_css_selector(locator)[index]
            else:
                element = self.driver.find_element_by_css_selector(locator)
        
        
        elif by == 'partialLinkText':
            if index:
                element = self.driver.find_element_by_partial_link_text(locator)[index]
            else:
                element = self.driver.find_element_by_partial_link_text(locator)
        
        elif by == 'linkText':
            if index:
                element = self.driver.find_elements_by_link_text(locator)[index]
            else:
                element = self.driver.find_element_by_link_text(locator)
        
        
        #deprecated
        elif by == 'tagName':
            if index:
                element = self.driver.find_elements_by_tag_name(locator)[index]
            else:
                element = self.driver.find_element_by_tag_name(locator)
        
        #deprecated
        elif by == 'name':
            if index:
                element = self.driver.find_elements_by_name(locator)[index]
            else:
                element = self.driver.find_element_by_name(locator)
        
        return element
    
    def _findElementsWithBy(self, by, locator):
        
        elements = None
        if by == 'id':
            elements = self.driver.find_elements_by_id(locator)
        
        elif by == 'accessibilityId':
            elements = self.driver.find_elements_by_accessibility_id(locator)
        
        elif by == 'className':
            elements = self.driver.find_elements_by_class_name(locator)
        
        elif by == 'xpath':
            elements = self.driver.find_elements_by_xpath(locator)
        
        elif by == 'uiaString':
            platform = self.getPlatform()
            if platform == 'ios':
                elements = self.driver.find_elements_by_android_uiautomator(locator)
            
            elif platform == 'android':
                elements = self.driver.find_elements_by_ios_uiautomation(locator) 
            
        
        elif by == 'predicateString':
            elements = self.driver.find_elemens_by_ios_predicate(locator)
        
        elif by == 'css':
            elements = self.driver.find_elements_by_css_selector(locator)
        
        
        elif by == 'partialLinkText':
            elements = self.driver.find_elements_by_partial_link_text(locator)
        
        elif by == 'linkText':
            elements = self.driver.find_elements_by_link_text(locator)
        
        
        #deprecated
        elif by == 'tagName':
            elements = self.driver.find_elements_by_tag_name(locator)
        
        #deprecated
        elif by == 'name':
            elements = self.driver.find_element_by_name(locator)
        
        return elements
    
    def clickElement(self,by,locator, index=0):
        try :
            element = self._findElementWithBy(by, locator, index)
            element.click()
        except:
            raise InvalidOperationException('Cannot click the element and by is %s, locator is %s, index is %d' % (by, locator, index))
            
    def clickElementAtCoordinates(self,coordinate_X, coordinate_Y):
        """ click element at a certain coordinate """
        self._info("Pressing at (%s, %s)." % (coordinate_X, coordinate_Y))
        action = TouchAction(self.driver)
        try :
            action.press(x=coordinate_X, y=coordinate_Y).release().perform()
        except:
            raise InvalidOperationException('Cannot click the element and coordinate_X is %s, coordinate_Y is %s' % (coordinate_X, coordinate_Y))
    
    def clickText(self,text, exact_match=False):
        
        if self.getPlatform() == 'ios':
            if exact_match:
                _xpath = u'//*[@value="{}" or @label="{}"]'.format(text, text)
            else:
                _xpath = u'//*[contains(@label,"{}") or contains(@value, "{}")]'.format(text, text)
                    
        elif self.getPlatform() == 'android':
            if exact_match:
                _xpath = u'//*[@{}="{}"]'.format('text', text)
            else:
                _xpath = u'//*[contains(@{},"{}")]'.format('text', text)
                
        self.clickELementByXpath(_xpath)
        
        
    def closeAllClient(self):
        for port in self.driverDict.keys():
            self.driverDict[port].quit()
            self.driverDict.pop(port)
        self.driver = None
    
    def closeClient(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            for port in self.driverDict.keys():
                if self.driverDict[port] == self.driver:
                    self.driverDict.pop(port)
        
    def elementAttributeShouldMatch(self, by, locator, index, attr_name, match_pattern, regexp=False):
        """Verify that an attribute of an element matches the expected criteria.

        The element is identified by _locator_. See `introduction` for details
        about locating elements. If more than one element matches, the first element is selected.

        The _attr_name_ is the name of the attribute within the selected element.

        The _match_pattern_ is used for the matching, if the match_pattern is
        - boolean or 'True'/'true'/'False'/'false' String then a boolean match is applied
        - any other string is cause a string match

        The _regexp_ defines whether the string match is done using regular expressions (i.e. BuiltIn Library's
        [http://robotframework.org/robotframework/latest/libraries/BuiltIn.html#Should%20Match%20Regexp|Should
        Match Regexp] or string pattern match (i.e. BuiltIn Library's
        [http://robotframework.org/robotframework/latest/libraries/BuiltIn.html#Should%20Match|Should
        Match])


        Examples:

        | Element Attribute Should Match | xpath = //*[contains(@text,'foo')] | text | *foobar |
        | Element Attribute Should Match | xpath = //*[contains(@text,'foo')] | text | f.*ar | regexp = True |
        | Element Attribute Should Match | xpath = //*[contains(@text,'foo')] | enabled | True |

        | 1. is a string pattern match i.e. the 'text' attribute should end with the string 'foobar'
        | 2. is a regular expression match i.e. the regexp 'f.*ar' should be within the 'text' attribute
        | 3. is a boolead match i.e. the 'enabled' attribute should be True


        _*NOTE: *_
        On Android the supported attribute names are hard-coded in the
        [https://github.com/appium/appium/blob/master/godEyes/devices/android/bootstrap/src/io/appium/android/bootstrap/AndroidElement.java|AndroidElement]
        Class's getBoolAttribute() and getStringAttribute() methods.
        Currently supported (appium v1.4.11):
        _contentDescription, text, className, resourceId, enabled, checkable, checked, clickable, focusable, focused, longClickable, scrollable, selected, displayed_


        _*NOTE: *_
        Some attributes can be evaluated in two different ways e.g. these evaluate the same thing:

        | Element Attribute Should Match | xpath = //*[contains(@text,'example text')] | name | txt_field_name |
        | Element Name Should Be         | xpath = //*[contains(@text,'example text')] | txt_field_name |      |

        """
        elements = self._findElementsWithBy(by, locator, index)
        if len(elements) > 1:
            log('info',"CAUTION: '%s' matched %s elements - using the first element only" % (locator, len(elements)))

        attr_value = elements[0].get_attribute(attr_name)

        # ignore regexp argument if matching boolean
        if isinstance(match_pattern, bool) or match_pattern.lower() == 'true' or match_pattern.lower() == 'false':
            if isinstance(match_pattern, bool):
                match_b = match_pattern
            else:
                match_b = ast.literal_eval(match_pattern.title())

            if isinstance(attr_value, bool):
                attr_b = attr_value
            else:
                attr_b = ast.literal_eval(attr_value.title())

            self._bi.should_be_equal(match_b, attr_b)

        elif regexp:
            self._bi.should_match_regexp(attr_value, match_pattern,
                                         msg="Element '%s' attribute '%s' should have been '%s' "
                                             "but it was '%s'." % (locator, attr_name, match_pattern, attr_value),
                                         values=False)
        else:
            self._bi.should_match(attr_value, match_pattern,
                                  msg="Element '%s' attribute '%s' should have been '%s' "
                                      "but it was '%s'." % (locator, attr_name, match_pattern, attr_value),
                                  values=False)
        # if expected != elements[0].get_attribute(attr_name):
        #    raise AssertionError("Element '%s' attribute '%s' should have been '%s' "
        #                         "but it was '%s'." % (locator, attr_name, expected, element.get_attribute(attr_name)))
        log('info',"Element '%s' attribute '%s' is '%s' " % (locator, attr_name, match_pattern))
    
    def elementNameShouldBe(self, by, locator,index, expected):
        try:
            element = self._findElementWithBy(by, locator, index)
            if str(expected) != str(element.get_attribute('name')):
                raise AssertionError("Element '%s' name should be '%s' "
                                     "but it is '%s'." % (locator, expected, element.get_attribute('name')))
            log('info',"Element '%s' name is '%s' " % (locator, expected))
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))
    
    def elementShouldBeDisabled(self, by, locator,index=0):
        """Verifies that element identified with locator is disabled.

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        try:
            if self._findElementWithBy(by, locator, index).is_enabled():
                self.logSource()
                raise AssertionError("Element '%s' should be disabled "
                                     "but did not" % locator)
            log('info',"Element '%s' is disabled ." % locator)
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))
    
    def elementShouldBeEnabled(self, by, locator,index=0):
        """Verifies that element identified with locator is enabled.

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        try:
            if not self._findElementWithBy(by, locator, index).is_enabled():
                self.logSource()
                raise AssertionError("Element '%s' should be enabled "
                                     "but did not" % locator)
            log('info',"Element '%s' is enabled ." % locator)
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))
    
    def elementShouldBeSelected(self, by, locator,index=0):
        """Verifies that element identified with locator is selected.

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        try:
            if not self._findElementWithBy(by, locator, index).is_selected():
                self.logSource()
                raise AssertionError("Element '%s' should be selected "
                                     "but did not" % locator)
                log('info',"Element '%s' is selected ." % locator)
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))
    
    def elementShouldBeVisible(self, by, locator,index=0):
        """Verifies that element identified with locator is displayed.

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        if not self._findElementWithBy(by, locator, index).is_displayed():
            self.logSource()
            raise AssertionError("Element '%s' should be displayed "
                                 "but did not" % locator)
        log('info',"Element '%s' is displayed ." % locator)
    
    
    def _get_text(self, by, locator,index=0):
        try:
            element = self._findElementWithBy(by, locator, index)
            if element is not None:
                return element.text
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))
    
    
    def elementShouldContainText(self, by, locator,index,expected,message=''):
        """Verifies element identified by ``locator`` contains text ``expected``.

        If you wish to assert an exact (not a substring) match on the text
        of the element, use `Element Text Should Be`.

        Key attributes for arbitrary elements are ``id`` and ``xpath``. ``message`` can be used to override the default error message.

        New in AppiumLibrary 1.4.
        """
        self._info("Verifying element '%s' contains text '%s'."
                    % (locator, expected))
        actual = self._get_text(by, locator,index)
        if not expected in actual:
            if not message:
                message = "Element '%s' should have contained text '%s' but "\
                          "its text was '%s'." % (locator, expected, actual)
            raise AssertionError(message)
    
    def elementShouldNotContainText(self, by, locator,index,expected,message=''):
        """Verifies element identified by ``locator`` does not contain text ``expected``.

        ``message`` can be used to override the default error message.
        See `Element Should Contain Text` for more details.
        """
        self._info("Verifying element '%s' does not contain text '%s'."
                   % (locator, expected))
        actual = self._get_text(by, locator,index)
        if expected in actual:
            if not message:
                message = "Element '%s' should not contain text '%s' but " \
                          "it did." % (locator, expected)
            raise AssertionError(message)
    
    def elementTextShouldBe(self, by, locator,index,expected,message=''):
        """Verifies element identified by ``locator`` exactly contains text ``expected``.

        In contrast to `Element Should Contain Text`, this keyword does not try
        a substring match but an exact match on the element identified by ``locator``.

        ``message`` can be used to override the default error message.

        New in AppiumLibrary 1.4.
        """
        self._info("Verifying element '%s' contains exactly text '%s'."
                    % (locator, expected))
        try:
            element = self._findElementWithBy(by, locator, index)
            actual = element.text
            if expected != actual:
                if not message:
                    message = "The text of element '%s' should have been '%s' but "\
                              "in fact it was '%s'." % (locator, expected, actual)
                raise AssertionError(message)
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))
        
    def elementValueShouldBe(self, by, locator,index,expected):
        try:
            element = self._findElementWithBy(by, locator, index)
            if str(expected) != str(element.get_attribute('value')):
                raise AssertionError("Element '%s' value should be '%s' "
                                     "but it is '%s'." % (locator, expected, element.get_attribute('value')))
            log('info',"Element '%s' value is '%s' " % (locator, expected))
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))
        
        
    def getCurActivity(self):
        return self.driver.current_activity
        
    def getElementAttribute(self, by, locator, attribute):
        """Get element attribute using given attribute: name, value,...

        Examples:

        | Get Element Attribute | locator | name |
        | Get Element Attribute | locator | value |
        """
        elements = self._findElementsWithBy(by, locator)
        ele_len = len(elements)
        if ele_len == 0:
            raise AssertionError("Element '%s' could not be found" % locator)
        elif ele_len > 1:
            self._info("CAUTION: '%s' matched %s elements - using the first element only" % (locator, len(elements)))

        try:
            attr_val = elements[0].get_attribute(attribute)
            log('info', "Element '%s' attribute '%s' value '%s' " % (locator, attribute, attr_val))
            return attr_val
        except:
            raise AssertionError("Attribute '%s' is not valid for element '%s'" % (attribute, locator))
    
    def getElementLocation(self, by, locator, index=0):
        """Get element location

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        element = self._findElementWithBy(by, locator, index)
        element_location = element.location
        log('info', "Element '%s' location: %s " % (locator, element_location))
        return element_location
    
    def getElementSize(self, by, locator, index=0):
        """Get element size

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        element = self._findElementWithBy(by, locator, index)
        element_size = element.size
        log('info', "Element '%s' size: %s " % (locator, element_size))
        return element_size
    
    def getMatchingXpathCount(self,xpath):
        """Returns number of elements matching ``xpath``

        One should not use the `xpath=` prefix for 'xpath'. XPath is assumed.

        | *Correct:* |
        | ${count}  | Get Matching Xpath Count | //android.view.View[@text='Test'] |
        | Incorrect:  |
        | ${count}  | Get Matching Xpath Count | xpath=//android.view.View[@text='Test'] |

        If you wish to assert the number of matching elements, use
        `Xpath Should Match X Times`.

        """
        
        return len(self.driver.find_elements_by_xpath(xpath))
    
    def getNetworkConnectionStatus(self):
        return self.driver.network_connection
    
    
    def getAppiumSessionId(self):
        """Returns the current session ID as a reference"""
        print("Appium Session ID: " + self.driver.session_id)
        return self.driver.session_id
    
#     def getAppiumTimeout(self):
#         pass
    
    
    def getSource(self):
        """Returns the entire source of the current page."""
        return self.driver.page_source
    
    def getText(self, by, locator,index=0):
        """Get element text (for hybrid and mobile browser use `xpath` locator, others might cause problem)

        Example:

        | ${text} | Get Text | //*[contains(@text,'foo')] |

        New in AppiumLibrary 1.4.
        """
        text = self._get_text(by, locator,index)
        log('info',"Element '%s' text is '%s' " % (locator, text))
        return text
        
    
    def goBack(self):
        return self.driver.back()
    
    def goToUrl(self,url):
        self.driver.get(url)
    
    def hideKeyboard(self,key_name=None, key=None, strategy=None):
        self.driver.hide_keyboard(key_name, key, strategy)
    
    def _element_input_text_by_locator(self, by, locator, index, text):
        try:
            element = self._findElementWithBy(by, locator, index)
            element.send_keys(text)
        except Exception:
            raise InvalidOperationException('can not input text by locator:%s' % locator)
    
    def _element_input_value_by_locator(self, by, locator, index, text):
        try:
            element = self._findElementWithBy(by, locator, index)
            element.set_value(text)
        except Exception:
            raise InvalidOperationException('can not input value by locator:%s' % locator)
       
    
    def inputText(self, by, locator, index, text):
        """Types the given `text` into text field identified by `locator`.

        See `introduction` for details about locating elements.
        """
        log('info',"Typing text '%s' into text field '%s'" % (text, locator))
        self._element_input_text_by_locator(by, locator, index, text)
    
    def inputValue(self, by, locator, index, text):
        """Sets the given value into text field identified by `locator`. This is an IOS only keyword, input value makes use of set_value

        See `introduction` for details about locating elements.
        """
        log('info',"Setting text '%s' into text field '%s'" % (text, locator))
        self._element_input_value_by_locator(by, locator, index, text)
    
    def landscape(self):
        return self.landscape()
    
    def lock(self,seconds=5):
        self.driver.lock(seconds)
    
    def longPressElement(self, by, locator, index=0):
        """ Long press the element """
        try:
            element = self._findElementWithBy(by, locator, index)
            long_press = TouchAction(self.driver).long_press(element)
            long_press.perform()
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))  
    
    def longPressKeycode(self, keycode, metastate=None):
        self.driver.long_press_keycode(keycode, metastate)
    
    def openClient(self, port=4723, **kwargs):
        desired_caps = kwargs
        remote_url = baseUrl + ':'  + str(port) + '/wd/hub'
        driver = webdriver.Remote(str(remote_url), desired_caps)
        self.driver = driver
        self.driverDict[port] = driver
        self.implicitlyWait(1)
    
    def pageShouldContainElement(self, by, locator):
        """Verifies that current page contains `locator` element.

        If this keyword fails, it automatically logs the page source
        """
        if not self._is_element_present(by, locator):
            self.logSource()
            raise AssertionError("Page should have contained element '%s' "
                                 "but did not" % locator)
        log('info',"Current page contains element '%s'." % locator)
    
    
    def pageShouldNotContainElement(self, locator):
        """Verifies that current page not contains `locator` element.

        If this keyword fails, it automatically logs the page source
        Giving `NONE` as level disables logging.
        """
        if self._is_element_present(locator):
            self.logSource()
            raise AssertionError("Page should not have contained element '%s' "
                                 "but did not" % locator)
        log('info',"Current page does not contains element '%s'." % locator)
    
    def pageShouldContainText(self, text):
        """Verifies that current page contains `text`.

        If this keyword fails, it automatically logs the page source
        Giving `NONE` as level disables logging.
        """
        if not self._is_text_present(text):
            self.logSource()
            raise AssertionError("Page should have contained text '%s' "
                                 "but did not" % text)
        log('info',"Current page contains text '%s'." % text)
        
    
    def pageShouldNotContainText(self, text):
        """Verifies that current page not contains `text`.

        If this keyword fails, it automatically logs the page source
        Giving `NONE` as level disables logging.
        """
        if self._is_text_present(text):
            self.logSource()
            raise AssertionError("Page should not have contained text '%s' "
                                 "but did not" % text)
        log('info',"Current page does not contains text '%s'." % text)
    
    
    
    def pinch(self, by, locator, index=0, percent=200, steps=1):
        """
        Pinch in on an element a certain amount.
        """
        try:
            element = self._findElementWithBy(by, locator, index)
            self.driver.pinch(element=element, percent=percent, steps=steps)
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))
    
    def portrait(self):
        self.driver.portrait()
    
    def pressKeycode(self, keycode, metastate=None):
        self.driver.press_keycode(keycode, metastate)
    
    def press_enter_keycode(self):
        self.driver.press_keycode(23)
        
    def press_up_keycode(self):
        self.driver.press_keycode(19)
        
    def press_down_keycode(self):
        self.driver.press_keycode(20)
    
    def press_left_keycode(self):
        self.driver.press_keycode(21)
    
    def press_right_keycode(self):
        self.driver.press_keycode(22)
    
    def press_back_keycode(self):
        self.driver.press_keycode(4)
    
    def press_home_keycode(self):
        self.driver.press_keycode(3)
    
    def press_search_keycode(self):
        self.driver.press_keycode(84)
    
    def press_power_keycode(self):
        self.driver.press_keycode(26)
    
    def press_menu_keycode(self):
        self.driver.press_keycode(82)
    
    def pullFile(self, path, decode=False):
        theFile = self.driver.pull_file(path)
        if decode:
            theFile = base64.b64decode(theFile)
        return theFile
    
    def pullFolder(self, path, decode=False):
        theFolder = self.driver.pull_folder(path)
        if decode:
            theFolder = base64.b64decode(theFolder)
        return theFolder
    
    def pushFile(self, path, data, encode=False):
        if encode:
            data = base64.b64encode(data)
        self.driver.push_file(path, data)
 
    
    def removeApplication(self, application_id):
        self.driver.remove_app(application_id) 
        
    def resetApplication(self):
        self.driver.reset()
    
    def scroll(self, start_by, start_locator, start_index, end_by, end_locator, end_index):
        """
        Scrolls from one element to another
        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        el1 = self._findElementWithBy(start_by, start_locator, start_index)
        el2 = self._findElementWithBy(end_by, end_locator, end_index)
        self.driver.scroll(el1, el2)
        
    
    def scrollDown(self, by, locator, index=0):
        """Scrolls down to element"""
        try:
            element = self._findElementWithBy(by, locator, index)
            self.driver.execute_script("mobile: scroll", {"direction": 'down', 'element': element.id})
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))
        
        
    def scrollUp(self, by, locator, index=0):
        try:
            element = self._findElementWithBy(by, locator, index)
            self.driver.execute_script("mobile: scroll", {"direction": 'up', 'element': element.id})
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))      

#     def setAppiumTimeout(self, seconds):
#         pass
    
    def setNetworkConnectionStatus(self, connectionStatus):
        """Sets the network connection Status.

        Android only.

        Possible values:
            | =Value= | =Alias=          | =Data= | =Wifi= | =Airplane Mode=  |
            |  0      | (None)           | 0      |   0    | 0                |
            |  1      | (Airplane Mode)  | 0      |   0    | 1                |
            |  2      | (Wifi only)      | 0      |   1    | 0                |
            |  4      | (Data only)      | 1      |   0    | 0                |
            |  6      | (All network on) | 1      |   1    | 0                |
        """
        return self.driver.set_network_connection(int(connectionStatus))
    
    def shake(self):
        self.driver.shake()
    
    def startActivity(self,appPackage, appActivity, **opts):
        """Opens an arbitrary activity during a test. If the activity belongs to
        another application, that application is started and the activity is opened.

        Android only.

        - _appPackage_ - The package containing the activity to start.
        - _appActivity_ - The activity to start.
        - _appWaitPackage_ - Begin automation after this package starts (optional).
        - _appWaitActivity_ - Begin automation after this activity starts (optional).
        - _intentAction_ - Intent to start (opt_ional).
        - _intentCategory_ - Intent category to start (optional).
        - _intentFlags_ - Flags to send to the intent (optional).
        - _optionalIntentArguments_ - Optional arguments to the intent (optional).
        - _stopAppOnReset_ - Should the app be stopped on reset (optional)?

        """


        # Almost the same code as in appium's start activity,
        # just to keep the same keyword names as in open application

        arguments = {
            'app_wait_package': 'appWaitPackage',
            'app_wait_activity': 'appWaitActivity',
            'intent_action': 'intentAction',
            'intent_category': 'intentCategory',
            'intent_flags': 'intentFlags',
            'optional_intent_arguments': 'optionalIntentArguments',
            'stop_app_on_reset': 'stopAppOnReset'
        }

        data = {}

        for key, value in arguments.items():
            if value in opts:
                data[key] = opts[value]

        self.driver.start_activity(app_package=appPackage, app_activity=appActivity, **data)
    
    def swipe(self,start_x, start_y, offset_x, offset_y, duration=1000):
        """
        Swipe from one point to another point, for an optional duration.

        Args:
         - start_x - x-coordinate at which to start
         - start_y - y-coordinate at which to start
         - offset_x - x-coordinate distance from start_x at which to stop
         - offset_y - y-coordinate distance from start_y at which to stop
         - duration - (optional) time to take the swipe, in ms.

        Usage:
        | Swipe | 500 | 100 | 100 | 0 | 1000 |

        *!Important Note:* Android `Swipe` is not working properly, use ``offset_x`` and ``offset_y``
        as if these are destination points.
        """
        self.driver.swipe(start_x, start_y, offset_x, offset_y, duration)
    
    def switchDriver(self, port):
        try:
            return self.getDriver(port)
        except Exception as e:
            print e
            #如果是不存在driverDict的port，会新建client
            self.openClient(port)
            return self.driver
    
    def getCurContext(self):
        return self.driver.current_context()
    
    def switchContext(self, contextName):
        self.driver.context(contextName)
    
    def getSettings(self):
        return self.driver.get_settings()
    
    def tap(self, by, locator, index=0, x_offset=None, y_offset=None, count=1):
        """ Tap element identified by ``locator``.

        Args:
        - ``x_offset`` - (optional) x coordinate to tap, relative to the top left corner of the element.
        - ``y_offset`` - (optional) y coordinate. If y is used, x must also be set, and vice versa
        - ``count`` - can be used for multiple times of tap on that element
        """
        try:
            el = self._findElementWithBy(by, locator, index)
            action = TouchAction(self.driver)
            action.tap(el,x_offset,y_offset, count).perform()
    
            el = self._findElementWithBy(by, locator, index)
            action = TouchAction(self.driver)
            action.tap(el).perform()
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))
            
    def getActivity(self):
        return self.driver.current_activity
    
    def waitActivity(self,activity, timeout=7, interval=1):
        """Wait for an activity: block until target activity presents
        or time out.

        Android only.

         - _activity_ - target activity
         - _timeout_ - max wait time, in seconds
         - _interval_ - sleep interval between retries, in seconds
        """

        if '/' in activity:
            rets = activity.split('/')
            if rets[1].startswith('.'):
                activity = rets[0] + rets[1]
            else:
                activity = rets[1]

        if not self.driver.wait_activity(activity=activity, timeout=float(timeout), interval=float(interval)):
            raise TimeoutException(msg="Activity %s never presented, current activity: %s" % (activity, self.getActivity()))
    
    def _wait_until_no_error(self, timeout, wait_func, *args):
        timeout = int(timeout)
        maxtime = time.time() + timeout
        while True:
            timeout_error = wait_func(*args)
            if not timeout_error:
                return
            if time.time() > maxtime:
                self.logSource()
                raise AssertionError(timeout_error)
            time.sleep(0.2)
    
    def _wait_until(self, timeout, error, function, *args):
        error = error.replace('<TIMEOUT>', str(timeout))

        def wait_func():
            return None if function(*args) else error

        self._wait_until_no_error(timeout, wait_func)

    def logSource(self):
        """Logs and returns the entire html source of the current page or frame.
        """
        
        source =  self.driver.page_source
        log('info',source)
        return source
    
    def _is_visible(self, by, locator, index):
        element = self._findElementWithBy(by, locator, index)
        if element is not None:
            return element.is_displayed()
        
    
    def waitUntilElementIsVisible(self, by, locator, index=0, timeout=7, error=None):
        def check_visibility():
            visible = self._is_visible(by, locator, index)
            if visible:
                return
            elif visible is None:
                return error or "Element locator '%s' did not match any elements after %s" % (locator, self._format_timeout(timeout))
            else:
                return error or "Element '%s' was not visible in %s" % (locator, self._format_timeout(timeout))
        self._wait_until_no_error(timeout, check_visibility, by, locator, index)

    def _is_text_present(self, text):
        text_norm = normalize('NFD', text)
        source_norm = normalize('NFD', self.getSource())
        return text_norm in source_norm
    
   
    
    def waitUntilPageContains(self,text, timeout=7, error=None):
        """Waits until `text` appears on current page.

        Fails if `timeout` expires before the text appears. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Page Does Not Contain`,
        `Wait Until Page Contains Element`,
        `Wait Until Page Does Not Contain Element` and
        BuiltIn keyword `Wait Until Keyword Succeeds`.
        """
        if not error:
            error = "Text '%s' did not appear in <TIMEOUT>" % text
        self._wait_until(timeout, error, self._is_text_present, text)
    
    
    
    def WaitUntilPageDoesNotContain(self,text, timeout=7, error=None):
        """Waits until `text` disappears from current page.

        Fails if `timeout` expires before the `text` disappears. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Page Contains`,
        `Wait Until Page Contains Element`,
        `Wait Until Page Does Not Contain Element` and
        BuiltIn keyword `Wait Until Keyword Succeeds`.
        """

        def check_present():
            present = self._is_text_present(text)
            if not present:
                return
            else:
                return error or "Text '%s' did not disappear in %s" % (text, self._format_timeout(timeout))

        self._wait_until_no_error(timeout, check_present)
    
    def _is_element_present(self, by, locator):
        elements = self._findElementsWithBy(by, locator)
        return len(elements) > 0
    
    def waitUntilPageContainsElement(self, by, locator, timeout=7, error=None):
        """Waits until element specified with `locator` appears on current page.

        Fails if `timeout` expires before the element appears. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Page Contains`,
        `Wait Until Page Does Not Contain`
        `Wait Until Page Does Not Contain Element`
        and BuiltIn keyword `Wait Until Keyword Succeeds`.
        """
        if not error:
            error = "Element '%s' did not appear in <TIMEOUT>" % locator
        self._wait_until(timeout, error, self._is_element_present, by, locator)
    
    
    
    
    def waitUntilPageDoesNotContainElement(self, by, locator, timeout=None, error=None):
        """Waits until element specified with `locator` disappears from current page.

        Fails if `timeout` expires before the element disappears. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Page Contains`,
        `Wait Until Page Does Not Contain`,
        `Wait Until Page Contains Element` and
        BuiltIn keyword `Wait Until Keyword Succeeds`.
        """

        def check_present():
            present = self._is_element_present(by, locator)
            if not present:
                return
            else:
                return error or "Element '%s' did not disappear in %s" % (locator, int(timeout))

        self._wait_until_no_error(timeout, check_present)
    
    def xpathShouldMatchXTimes(self,xpath, count):
        """Returns number of elements matching ``xpath``

        One should not use the `xpath=` prefix for 'xpath'. XPath is assumed.

        | *Correct:* |
        | ${count}  | Get Matching Xpath Count | //android.view.View[@text='Test'] |
        | Incorrect:  |
        | ${count}  | Get Matching Xpath Count | xpath=//android.view.View[@text='Test'] |

        If you wish to assert the number of matching elements, use
        `Xpath Should Match X Times`.

        """
        assert count == self.getMatchingXpathCount(xpath)
    
    def zoom(self, by, locator, index=0, percent=200, steps=50):
        try:
            element = self._findElementWithBy(by, locator, index)
            self.driver.zoom(element, percent, steps)
        except:
            raise InvalidOperationException('Cannot find the element and by is %s, locator is %s, index is %d' % (by, locator, index))
    
    #-------------------------———————取代AppiumLibrary———————————————————————————————————————
    
    def activateImeEngine(self, engine):
        self.driver.activate_ime_engine(engine)
    
    def getCurActiveImeEngine(self):
        return self.driver.active_ime_engine()
    
    def addCookie(self,cookie_dict):
        return self.driver.add_cookie(cookie_dict)
    
    def app_strings(self,language, string_file):
        return self.driver.app_strings(language, string_file)
    
    def applicationCache(self):
        return self.driver.application_cache
    
        
    
    def getCurrentUrl(self):
        return self.driver.current_url
        
    
    def deleteCookie(self, name):
        self.driver.delete_cookie(name)
        
    def deleteAllCookie(self):
        self.driver.delete_all_cookies() 
        
    def getDeviceTime(self):
        return self.driver.device_time()
    
    def closeCurWindow(self):
        self.driver.close()
    
    def closeRunningApp(self):
        self.driver.close_app()
    
    def deactivateIMEEngine(self):
        self.driver.deactivate_ime_engine()
    
    
    def forward(self):
        self.driver.forward()
        
    def openNotifications(self):
        self.driver.open_notifications()
    
    def getNetworkConnection(self):
        return self.driver.network_connection()
        
    def getOrientation(self):
        return self.driver.orientation
    
    def installApp(self, app_path):
        self.driver.install_app(app_path)
    
    def isAppInstalled(self, bundle_id):
        return self.driver.is_app_installed(bundle_id)
    
    def setOrientation(self, value):
        return self.driver.orientation(value)
    
    def launchApp(self):
        self.driver.launch_app()
        
        
    def toggleLocationServices(self):
        self.driver.toggle_location_services()
        
    def toutchId(self, match):
        self.driver.touch_id(match)
    
    def getBrowserName(self):
        return self.driver.name()
    
    

    
    def getWindowHandles(self):
        return self.driver.window_handles()  
    
       
        
    def getWindowPosition(self, windowHandle=None):
        if windowHandle:
            windowHandle = self.driver.current_window_handle()
        return self.driver.get_window_position(windowHandle)
        
    def getWindowSize(self, windowHandle=None):
        if windowHandle:
            windowHandle = self.driver.current_window_handle()
        return self.driver.get_window_size(windowHandle)
    
    def refresh(self):
        self.driver.refresh()
        
    def setLocation(self, latitude, longitude, altitude):
        self.driver.set_location(latitude, longitude, altitude)
    
    def setNetworkConnection(self, connectionType):
        self.driver.set_network_connection(connectionType)
        
    def updateSettings(self, settings):
        self.driver.update_settings(settings)
    
    def setWindowPosition(self, position_X, position_Y, windowHandle=None):
        if windowHandle:
            windowHandle = self.driver.current_window_handle()
        return self.driver.set_window_position(position_X, position_Y, windowHandle)
        
    def setWindowSize(self, width, height, windowHandle=None):
        if windowHandle:
            windowHandle = self.driver.current_window_handle()
        return self.driver.set_window_size(width, height, windowHandle)
    
    
     
    def maximizeWindow(self):
        self.driver.maximize_window()
    
       
    #-------------------------———————除了AppiumLibrary以外支持的特性———————————————————————————————————————
    
    
    def waitForActivity(self, activityName, timeout=7):
        begin = time.time()
        retryCount = int(timeout)
        timeout = int(timeout)
        for i in range(1, retryCount):
            print "waitForTopActivity current retrycount:%d" % i 
            curTopActivityName = self.driver.current_activity
            if (curTopActivityName == activityName):
                print 'waitForTopActivity %s match' % activityName
                break
            time.sleep(1)
            leftTime = time.time() - begin
            assert timeout and  leftTime < timeout, 'waitForTopActivity %s timeout' % activityName
            assert i < retryCount - 1, 'waitForTopActivity %s has run out of retry times and not match' % activityName    
        time.sleep(5)
    
    def _doClick(self,element,locator,index):
        try:
            element.click()
        except:
            raise InvalidOperationException('Cannot click the %s element locator:"%s" and index:%d' % (locator,index))
    
    def clickELementByXpath(self, xpath, index=0):
        element = None
        if index:
            element = self.driver.find_elements_by_xpath(xpath)[index]
        else:
            element = self.driver.find_element_by_xpath(xpath)
        
        self._doClick(element, xpath, index)
   
    
    
    
    def clickELementById(self,_id, index=0):
        element = None
        if index:
            element = self.driver.find_elements_by_id(_id)[index]
        else:
            element = self.driver.find_element_by_id(_id)
        self._doClick(element, _id, index)
    
    def clickElementByAccessibilityId(self,accessibility_id, index=0):
        element = None
        if index:
            element = self.driver.find_elements_by_accessibility_id(id)[index]
        else:
            element = self.driver.find_element_by_accessibility_id(id)
        self._doClick(element, accessibility_id, index)
    
    
    
if __name__ == '__main__':
    from AppiumService import AppiumService
    from Cli import Cli
    cli = Cli('192.168.1.105')
#     #通过adb获取相关参数填进
    s = AppiumService()
    s.startServer()
    appium = AppiumClient()
    appium.openClient(platformName='Android',deviceName='magicBox2',appPackage='com.yunos.tv.yingshi.boutique',appActivity='com.yunos.tv.yingshi.activity.YingshiHomeActivity', noReset='true')
    time.sleep(5)
    cli.startActivityWithURI('yunostv_yingshi://yingshi_detail/?id=158366')
    cli.waitForTopActivity('com.yunos.tv.yingshi.activity.YingshiDetailActivity')
    time.sleep(5)
    appium.clickElement('//android.view.View[@resource-id="com.yunos.tv.yingshi.boutique:id/leftlay_list"]/com.yunos.tv.app.widget.FrameLayout[@index=0]')
#     appium.clickByXpath("//android.view.View[@resource-id='com.yunos.tv.yingshi.boutique:id/leftlay_list']/com.yunos.tv.app.widget.FrameLayout[@index=0]")
#     appium.closeClient()
    s.stopServer()
#     driver = appium.get_driver()
#     time.sleep(5)
#     by = By.ID


#     #浏览器相关
#     driver.back()
# #     driver.find_element_by_css_selector(css_selector)
# #     driver.find_element_by_id(id_)
# #     driver.find_element_by_link_text(link_text)
# #     driver.find_element_by_name(name)
# #     driver.find_element_by_partial_link_text(link_text)
# #     driver.find_elements_by_tag_name(name)
# #     driver.find_elements_by_xpath(xpath)
# #     driver.keyevent(23)
# #     print 'driver'
#     print driver.current_activity
# #     ac =driver.background_app(5)
#     time.sleep(10)
#     print 'done'

