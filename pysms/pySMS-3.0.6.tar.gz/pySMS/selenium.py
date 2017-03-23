# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 14:08:50 2016

@author: doarni
"""
import os
import time
import json
import configparser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import *
from selenium.webdriver.common.action_chains import ActionChains
from pySMS.livery import tables as lv
from pySMS.prompts import prompts as pmt
from pySMS.ui.tk import widget
from pySMS.handlers import Handles
from pySMS.utils.logger import Logger
from pySMS.utils.logic.webpage import Webpage
from pySMS.utils.excepetions import NoRecordsFoundError, WaitTimeOutError, ProductChooserAddError, MissingInformationError
from pySMS.utils.page.waits import Waits
from pySMS.utils.page.changesite import ChangeSite
import pySMS.html.pathdata.loginPage as loginpage
import pySMS.html.pathdata.mainPage as mainpage
import pySMS.html.pathdata.prodChooser as stprodchooser
import pySMS.html.pathdata.stockTabMutate as stmutate
import pySMS.html.pathdata.stockTabTable as sttable
import pySMS.html.pathdata.stockTab as st
import pySMS.html.pathdata.userSettings as uS
import pySMS.html.pathdata.adjustStock as adj
from colorama import init, Fore

init(autoreset=True)


class macros():
    
    def __init__(self, name, pause_at_launch=False):
        self.name = name
        self.pause_at_launch= pause_at_launch
        self.driver = None
        self.waits = None
        self.change = None
        self.path = os.path.dirname(os.path.realpath(__file__))

        self.web_logic = Webpage.Logic()
        self.w = widget()
        self.handles = Handles()
        self.err = self.handles.Errors()
        self.jdata = self.handles.Data()
        self.logger = Logger(self.name)

        self.log_list_info = []
        self.log_list_error = []
        self.log_list_warning = []
        self.log_list_critical = []
        self.log_list_debug = []

        self.logininfo = []
        self.current_func_data = {}

        self.actions = None

        self.siteData = self.jdata.load_json_data()

        self.current_error_count = 0
        self.adjustmentErrCount = 0

    def parse_settings_for(self, section, value):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        try:
            return config.get(section, value)
        except:
            return None

    def check_for_login_information(self):
        username = self.parse_settings_for('USER', 'username')
        password = self.parse_settings_for('USER', 'password')

        if username.upper() == 'NONE' and password.upper() == 'NONE':
            return {'exists': False, 'username': username, 'password': password}
        else:
            return {'exists': True, 'username': username, 'password': password}

    def log(self, _type, text):
        try:
            if _type.lower() == 'info':
                self.log_list_info.append(text)

            if _type.lower() == 'error':
                self.log_list_error.append(text)

            if _type.lower() == 'warning':
                self.log_list_warning.append(text)

            if _type.lower() == 'critical':
                self.log_list_critical.append(text)

            if _type.lower() == 'debug':
                self.log_list_debug.append(text)

            self.current_func_data['info'] = self.log_list_info
            self.current_func_data['error'] = self.log_list_error
            self.current_func_data['warning'] = self.log_list_warning
            self.current_func_data['critical'] = self.log_list_critical
            self.current_func_data['debug'] = self.log_list_debug

        except Exception as e:
            pass

    def write_log(self):
        try:
            self.logger.write_log_file(self.current_func_data)
        except Exception as e:
            pass

    def reportMutationErrors(self):
        return self.current_error_count

    def slay(self):
        print(Fore.RED + 'Disconnecting From SMS')
        self.log('info', '[INFO] Shutting down Webdriver')
        self.driver.quit()
        print(Fore.RED + 'Disconnected')
        self.log('info', '[INFO] Webdriver closed')

    def var(self): #must be called var, driver is not defined till launch call
        self.css = self.driver.find_element_by_css_selector

    def _wait(self, n):
        time.sleep(n)

    def launch(self):
        if self.check_for_login_information()['exists'] == False:
            raise MissingInformationError('user', ['username', 'password'], msg="Missing login information. Please configure this in settings.")
        else:
            chromedriver = self.path + "\\chromedriver.exe"
            os.environ["webdriver.chrome.driver"] = chromedriver
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
            self.driver = webdriver.Chrome(chromedriver)
            print('SESSION_URL = ' + self.driver.command_executor._url)
            print('SESSION_ID = ' + self.driver.session_id)
            self.driver.maximize_window()
            self.driver.get(loginpage.url)
            self.wait = Waits(self.driver)

        if self.pause_at_launch != False:
            self.err.err_basic("Please press 'OK' when the page has fully loaded!", "SMSA")

    def hook_launch(self, url, session_id):
        if self.check_for_login_information()['exists'] == False:
            raise MissingInformationError('user', ['username', 'password'], msg="Missing login information. Please configure this in settings.")
        chromedriver = self.path + "\\chromedriver.exe"
        os.environ["webdriver.chrome.driver"] = chromedriver
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        self.driver = webdriver.Remote(command_executor=url, desired_capabilities=options.to_capabilities())
        self.driver.close()
        self.driver.session_id = session_id
        print('SESSION_URL = ' + self.driver.command_executor._url)
        print('SESSION_ID = ' + self.driver.session_id)
        self.driver.maximize_window()
        self.driver.get(loginpage.url)

    def input_to_element(self, selector, text):
        self.actions = ActionChains(self.driver)
        self.search = self.css(selector)
        self.search.click()
        self.clickinto = self.actions.move_to_element(self.search).send_keys(text + Keys.RETURN).perform()
        self.actions = None

    def get_inner_html(self, selector):
        return self.css(selector).get_attribute('innerHTML')

    def getHTMLLoginPage(self):
        print(Fore.YELLOW + 'Grabbing html info from login page')
        time.sleep(1)
        with open(self.path + '//html//login.html', 'w')as f:
            f.write(self.driver.page_source)
        f.close()
        print(Fore.YELLOW + 'Done.')
        print(Fore.YELLOW + 'Saved as login.html')

    def getHTML(self, filename):
        print(Fore.YELLOW + 'Grabbing html info from page')
        time.sleep(1)
        with open(self.path + '//html//' + filename,'w')as f:
            f.write(self.driver.page_source)
        f.close()
        print(Fore.YELLOW + 'Done.')
        print(Fore.YELLOW + 'Saved as ' + filename)
    
    def getHTMLMainPage(self):
        # used to grab HTML info from the site after logging in
        print(Fore.YELLOW + 'Grabbing html info from page')
        time.sleep(1)
        with open(self.path + '//html//main.html','w')as f:
            f.write(self.driver.page_source)
        f.close()
        print(Fore.YELLOW + 'Done.')
        print(Fore.YELLOW + 'Saved as main.html')

    def login(self):
        time.sleep(1)
        print(Fore.YELLOW + 'Logging in as ' + self.parse_settings_for('USER', 'username'))
        self.log('info', '[INFO] [DEBUG] Logging in as ' + self.parse_settings_for('USER', 'username'))
        self.change = ChangeSite(self.driver,
                                 self.parse_settings_for('USER', 'username'),
                                 self.parse_settings_for('USER', 'password'))
        try:
            self.wait.clear_input(loginpage.username)
            self.wait.send_keys_to(self.parse_settings_for('USER', 'username'), loginpage.username)
            self.wait.clear_input(loginpage.password)
            self.wait.send_keys_to(self.parse_settings_for('USER', 'password'), loginpage.password)
            try:
                self.wait.clickable(loginpage.loginbutton)
                print(Fore.YELLOW + 'Logged in successfully as ' + self.parse_settings_for('USER', 'username'))
                self.log('info', '[INFO] [DEBUG] Logged in successfully as ' + self.parse_settings_for('USER', 'username'))
            except Exception as _e:
                print(Fore.LIGHTRED_EX + 'Logged in Failed')
                print(Fore.LIGHTMAGENTA_EX + 'Traceback: ' + Fore.LIGHTRED_EX + str(_e))
                self.err.err_custom('Unable to login as ' + self.parse_settings_for('USER', 'username') + '. Please refresh the page and login manually.', 'Error', 'MB_OK', 'ICON_EXCLAIM')
                self.log('info', '[INFO] [ERROR] Unable to login as ' + self.parse_settings_for('USER', 'username') + '.')
                self.log('warning', str(_e))
        except Exception as e:
            print(Fore.LIGHTRED_EX + 'Logged in Failed')
            print(Fore.LIGHTMAGENTA_EX + 'Traceback: ' + Fore.LIGHTRED_EX + str(e))
            self.err.err_custom('Unable to login as ' + self.parse_settings_for('USER', 'username') + '. Please refresh the page and login manually.', 'Error', 'MB_OK', 'ICON_EXCLAIM')
            self.log('info', '[INFO] [ERROR] Unable to login as ' + self.parse_settings_for('USER', 'username') + '.')
            self.log('warning', str(e))

    def checksite(self):
        time.sleep(2)
        try:
            site = self.css(mainpage.checkSite).get_attribute('innerHTML')
            print(Fore.YELLOW + 'Logged into site ' + site + '\n')
            self.log('info', '[INFO] [DEBUG] Logged into site ' + site)
            return site
        except Exception as e:
            self.err.err_traceback(e,'Unable to check site you are logged in under, please verify this before continuing')
            self.log('info', '[INFO] [ERROR] Unable to check site you are logged in under, please verify this before continuing')
            self.log('warning', str(e))

    def change_site_strict(self, site):
        site_name = ('_'.join(site.split(' ')))
        for key, value in self.siteData['listBoxSites'].items():
            if site_name == str(key):
                self.driver.get(self.driver.current_url)
                self.login()
                self.change.change_site(site_name)

            if self.checksite == site:
                print(Fore.LIGHTYELLOW_EX + 'Successfully changed site to: ' + Fore.MAGENTA + site)
                self.log('info', '[INFO] [DEBUG] Successfully changed site to: ' + site)


    def change_site(self, site):
        site_name = ('_'.join(site.split(' ')))
        for key, value in self.siteData['listBoxSites'].items():
            if site_name == str(key):
                self.driver.get(self.driver.current_url)
                self.login()
                self.change.change_site(site_name)
                self.inventory_tab()
                self.stStockTabButton()

            if self.checksite == site:
                print(Fore.LIGHTYELLOW_EX + 'Successfully changed site to: ' + Fore.MAGENTA + site)
                self.log('info', '[INFO] [DEBUG] Successfully changed site to: ' + site)

    def testClick(self, css_selector):
        self.css(css_selector).click()

    def inventory_tab(self):
        try:
            self.wait_for_click(mainpage.InventoryTab)
        except Exception as e:
            self.err.err_basic('Unable to click Ribbon Button: Inventory Tab, please click the Ribbon Button: Inventory Tab then press ok to continue', 'Error')
            self.log('info', '[INFO] [ERROR] Unable to click on Ribbon Button: Inventory Tab'), self.log('warning', str(e))
            self.current_error_count += 1

    def stStockTabButton(self):
        try:
            self.wait_for_click(st.stStockTabButton)
        except Exception as e:
            self.err.err_basic('Unable to click Stock Tab button, please click the stock tab button then press ok to continue', 'Error')
            self.log('info', '[INFO] [ERROR] Unable to click on Stock Tab button'), self.log('warning', str(e))
            self.current_error_count += 1

    def stSearchButton(self):
        try:
            self.wait_for_click(st.stStockTabSearchButton)
        except Exception as e:
            self.err.err_basic('Unable to click search button, please click search button and click ok to continue', 'Error')
            self.log('info', '[INFO] [ERROR] Unable to click search button'), self.log('warning', str(e))
            self.current_error_count += 1

    def stProdChooserSelect(self):
        try:
            self.wait_for_click(stprodchooser.prodchooserSelect)
        except Exception as e:
            self.err.err_basic('Unable to open product chooser on stock page, please open and click ok to continue', 'Error')
            self.log('info', '[INFO] [ERROR] Unable to open product chooser on stock page'), self.log('warning', str(e))
            self.current_error_count += 1
            
    def stProdChooserSearch(self, item):
        try:
            self.actions = ActionChains(self.driver)
            self.search = self.css(stprodchooser.prodchooserSearchBar)
            self.search.click()
            self.clickinto = self.actions.move_to_element(self.search).send_keys(item + Keys.RETURN).perform()
            self.actions = None
        except Exception as e:
            self.err.err_basic('Unable to search for ' + item + ', please search and click ok to continue', 'Error')
            self.log('info', '[INFO] [ERROR] Unable to search for ' + item), self.log('warning', str(e))
            self.current_error_count += 1

    def stProdChooserAddItem(self, item_dict):
        def read_table(y_range):
            data_dict = {}
            try:
                for y in range(y_range[0], y_range[1] + 1):
                    for tr in self.driver.find_elements_by_css_selector(stprodchooser.prodChooserTRpathFront + str(y) + stprodchooser.prodChooserTRpathBack):
                        tds = tr.find_elements_by_tag_name('td')
                        if tds:
                            l = []
                            for td in tds:
                                try:
                                    l.append(td.text)
                                except:
                                    l.append('None')
                            data_dict['row' + str(y)] = l
                return data_dict
            except Exception as j:
                print(str(j))
        try:
            results_dict = self.web_logic.product_chooser_add_item(item_dict, read_table(self.getResults(stprodchooser.prodChooserResults)))
        except ProductChooserAddError as e:
            print("Unable to add item from product chooser! Item: " + item_dict['prodNumber'])
        try:
            for k, v in results_dict.items():
                if results_dict['action'] == 'none':
                    self.err.err_basic(results_dict['reason'], 'MatchError')
                if results_dict['action'] == 'click':
                    if results_dict['selector_count'] == 1:
                        self.wait_for_click(results_dict['selectors'][0])
                    if results_dict['selector_count'] == 2:
                        try:
                            self.wait_for_click(results_dict['selectors'][0])
                        except Exception as e:
                            self.wait_for_click(results_dict['selectors'][1])
        except Exception as e:
            self.err.err_full_traceback(e, 'Unable to add item: ' + item_dict['prodNumber'] + ' in prod chooser')
            self.log('info', '[INFO] [ERROR] Unable to add item: ' + item_dict['prodNumber'] + ' in prod chooser. Traceback: ' + str(e))


    def stProdChooserFinish(self):
        try:
            self.wait_for_click(stprodchooser.prodchooserFinishButton)
        except Exception as e:
            self.err.err_basic('Unable to click finish, please click finish and click ok to continue', 'Error')
            self.log('info', '[INFO] [ERROR] Unable to click finish'), self.log('warning', str(e))
            self.current_error_count += 1

    def getResults(self, _selector):
        self.wait_for(_selector)
        data = self.css(_selector).get_attribute('innerHTML')
        if data == 'Loading...':
            for _i in range(6):
                if _i < 5:
                    time.sleep(3)
                    data = self.css(_selector).get_attribute('innerHTML')
                    if data == 'Loading...':
                        continue
                    else:
                        if data != "No records":
                            data = data.split(' ')[0]
                            return [int(data.split('-')[0]), int(data.split('-')[1])]  # [min val, max val]
                        else:
                            return data
                elif _i >= 5:
                    self.err.err_custom('Could not get number of records returned.', 'Error', 'MB_OK', 'ICON_EXCLAIM')
                    break
        elif data != "No records":
            data = data.split(' ')[0]
            return [int(data.split('-')[0]), int(data.split('-')[1])] #[min val, max val]
        elif data == "No records":
            self.err.err_custom('No Records found for this item.', 'Error', 'MB_OK', 'ICON_EXCLAIM')
            self.log('info', '[INFO] No Records found for this item.')
            return data
        else:
            data = data.split(' ')[0]
            return [int(data.split('-')[0]), int(data.split('-')[1])] #[min val, max val]

    def go_back(self):
        self.driver.execute_script("window.history.go(-1)")

    def input_action_chain(self, delay=0.4, init_action=None, input_selector='None', input_text='None'):

        action_chain = init_action #Clears action chain
        time.sleep(delay)
        action_input_alias = self.css(input_selector)
        action_input_alias.click()
        action_chain = ActionChains(self.driver)
        action_chain.move_to_element(action_input_alias).send_keys(input_text).perform()
        action_chain = init_action #Clears action chain


    def stMutation(self, dict, data):
        #Click Mutate
        self.wait_for_click(stmutate.stMutateButton)

        #Adjust Quantity
        self.actions = None
        self.quantity = self.css(stmutate.stMutateQuantity)
        self.quantity.click()
        self.actions = ActionChains(self.driver)
        self.clickinto = self.actions.move_to_element(self.quantity).send_keys('1').perform()
        self.actions = None

        #Add Note
        self.actions = None
        self.note = self.css(stmutate.stMutateNote)
        self.note.click()
        self.actions = ActionChains(self.driver)
        self.clickinto = self.actions.move_to_element(self.note).send_keys(stmutate.stnote).perform()
        self.actions = None

        #click save, finish mutation
        try:
            self.wait_for_click(stmutate.stMutateSavebutton)
            time.sleep(2)
            print('Product: ' + dict['prodnumber'] + ' Lot: ' + dict['lot_serial'] + ' Case: ' + str(data[0]).rstrip('.0') + ' Successfully Mutated' + '\n')
            self.log('info', '[INFO] Product: ' + str(dict['prodnumber']) + ' Lot: ' + str(dict['lot_serial']) + ' Successfully Mutated')
            self.driver.execute_script("window.history.go(-1)")
            try:
                self.wait.sleep(1)
                self.css(stmutate.stMutateCancelButton).click()
            except:
                None #No cancel button, move on
            self.stStockTabButton()
        except Exception as e:
            self.err.err_basic('Unable to mutate Product: ' + dict['prodnumber'] + ' Lot: ' + dict['lot_serial'] + ' Case: ' + str(data[0]).rstrip('.0') + ', please mutate and hit enter to continue', 'Mutation Error')
            self.log('warning', '[CRITICAL ERROR] Unable to mutate Product: ' + str(dict['prodnumber']) + ' Lot: ' + str(dict['lot_serial']) + ' , please mutate and hit enter to continue')
            self.log('warning', str(e))


    def stTableCheckBoxes(self, N):
        self.wait_for_click(self.web_logic.stock_tab_table_checkboxes(N))

    def parse_stock_table(self):
        dr = self.getResults(st.stStockTabResults)
        results = {'total_rows': dr[1], "items": []}
        if 'No records' in dr:
            return "No Records Found"
        elif dr == None:
            raise NoRecordsFoundError('Stock Table range <' + str(type(dr)) + '>')
        else:
            pass
        for y in range(dr[0], dr[1] + 1):
            print(Fore.LIGHTYELLOW_EX + 'Parsing row: ' + str(y) + ' of ' + str(dr[1]))

            tableProdNumber = {"product": self.css(sttable.stTableProductFront + str(y) + sttable.stTableProductBack).get_attribute('innerHTML'), "path": sttable.stTableProductFront + str(y) + sttable.stTableProductBack}
            tableDescription = {"description": self.css(sttable.stTableDescriptionFront + str(y) + sttable.stTableDescriptionBack).get_attribute('innerHTML'), "path": sttable.stTableDescriptionFront + str(y) + sttable.stTableDescriptionBack}
            tableLotSerial = {"lot_serial": self.css(sttable.stTableLotSerialFront + str(y) + sttable.stTableLotSerialBack).get_attribute('innerHTML'), "path": sttable.stTableLotSerialFront + str(y) + sttable.stTableLotSerialBack}
            tableContainer = {"container": self.css(sttable.stTableContainerFront + str(y) + sttable.stTableContainerBackInfo).get_attribute('innerHTML'), "path": sttable.stTableContainerFront + str(y) + sttable.stTableContainerBackInfo}
            tableContainerType = {"container_type": self.css(sttable.stTableContainerFront + str(y) + sttable.stTableContainerBackType).get_attribute('innerHTML'),"path": sttable.stTableContainerFront + str(y) + sttable.stTableContainerBackType}
            tableLocation = {"location": self.css(sttable.stTableLocationFront + str(y) + sttable.stTableLocationBackInfo).get_attribute('innerHTML'), "path": sttable.stTableLocationFront + str(y) + sttable.stTableLocationBackInfo}
            tableLocationType = {"location_type": self.css(sttable.stTableLocationFront + str(y) + sttable.stTableLocationBackLocType).get_attribute('innerHTML'), "path": sttable.stTableLocationFront + str(y) + sttable.stTableLocationBackLocType}

            results["items"].append({"row": y ,"data": {"product_info": tableProdNumber,
                                                        "description_info": tableDescription,
                                                        "lot_serial_info": tableLotSerial,
                                                        "container_info": tableContainer,
                                                        "container_type_info": tableContainerType,
                                                        "location_info": tableLocation,
                                                        "location_type_info": tableLocationType}})

        return results

    def stTableParsing(self, dict, funcType, bins="No"):
        if bins == "No":
            data = [dict['caseNumber'], dict['lotNumber'], dict['serialNumber'], "none"]
        elif bins == "Yes":
            data = [dict['caseNumber'], dict['lotNumber'], dict['serialNumber'], dict['binlocation']]
        dr = self.getResults(st.stStockTabResults)
        if 'No records' in dr:
            raise NoRecordsFoundError('Stock Table range <' + str(dr[0]) + ' , ' + str(dr[1] + 1) + '>')
        elif dr == None:
            raise NoRecordsFoundError('Stock Table range <' + str(type(dr)) + '>')
        else:
            pass
        for y in range(dr[0], dr[1] + 1):
            print(Fore.LIGHTYELLOW_EX + 'Parsing row: ' + str(y) + ' of ' + str(dr[1]))
            tableProdNumber = self.css(sttable.stTableProductFront + str(y) + sttable.stTableProductBack).get_attribute('innerHTML')
            tableDescription = self.css(sttable.stTableDescriptionFront + str(y) + sttable.stTableDescriptionBack).get_attribute('innerHTML')
            tableLotSerial = self.css(sttable.stTableLotSerialFront + str(y) + sttable.stTableLotSerialBack).get_attribute('innerHTML')
            tableContainer = self.css(sttable.stTableContainerFront + str(y) + sttable.stTableContainerBackInfo).get_attribute('innerHTML')
            tableLocation = self.css(sttable.stTableLocationFront + str(y) + sttable.stTableLocationBackInfo).get_attribute('innerHTML')
            tableLocationType = self.css(sttable.stTableLocationFront + str(y) + sttable.stTableLocationBackLocType).get_attribute('innerHTML')

            if funcType == 'mutation':
                _result = self.stBoolDataMutation({'rowNumber': str(y), 'prodnumber': tableProdNumber, 'description': tableDescription, 'lot_serial': tableLotSerial,
                                                   'container': tableContainer, 'location': tableLocation, 'location_type': tableLocationType}, data)
                if _result == True:
                    return True
                    break
                elif _result == False:
                    if y >= dr[1] + 1:
                        return False

    def stBoolDataMutation(self, dict, data):
        _return = None
        results = self.web_logic.bool_data_from_table(dict, data)
        if results == None:
            _return = False
            pass
        if results['match_found'] == True:
            print(Fore.LIGHTGREEN_EX + 'Found Match!' + '\n')
            lv.formatListToTable(dict, lv.formatDictotList(dict), Fore.LIGHTYELLOW_EX)
            self.wait_for_click(results['data']['checkbox_selector'])
            try:
                self.stMutation(dict, data)
                _return = True
                return _return
            except Exception as e:
                self.current_error_count += 1
                self.err.err_traceback(e, 'Unable to mutate Product: ' + dict['prodnumber'] + ' Lot: ' + dict['lot_serial'] + ' Case: ' + str(data[1]).rstrip('.0') + ', please mutate and hit enter to continue')
                self.log('warning', '[CRITICAL ERROR] Unable to mutate Product: ' + str(dict['prodnumber']) + ' Lot: ' + str(dict['lot_serial']))
                _return = False
        if results['match_found'] == False:
            _return = False
        return _return

    def wait_for_click(self, selector):
        self.wait.clickable(selector)

    def wait_for(self, selector):
        self.wait.to_exist(selector)

    def mutate(self, _dict):

        product_number = _dict['productNumber']
        self.stProdChooserSelect()

        self.stProdChooserSearch(product_number)

        self.stProdChooserAddItem({'prodNumber': _dict['productNumber'], 'description': _dict['description']})

        self.stProdChooserFinish()
        self.stSearchButton()

        try:
            _results = self.stTableParsing(_dict, 'mutation', bins=_dict['bin?'])
            if _results != True:
                self.err.err_custom('Item Product: ' + _dict['productNumber'] + ', was never mutated. Please resolve the issue manually.', 'Alert!', 'MB_OK', 'ICON_EXCLAIM')
                self.log('warning', 'Item Product: ' + _dict['productNumber'] + ', was never mutated. Please resolve the issue manually.')
        except Exception as e:
            print(Fore.LIGHTRED_EX + 'Failed to parse table. Skipping item [{}]'.format(_dict['productNumber']))
            print(Fore.LIGHTMAGENTA_EX + str(e))
