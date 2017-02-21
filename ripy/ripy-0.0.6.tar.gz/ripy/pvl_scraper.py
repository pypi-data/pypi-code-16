import glob
import os
import time

from selenium import webdriver


# region Waiting logic

class wait_for_page_load(object):
    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html').text

    def page_has_loaded(self):
        new_page = find_element_safe(self.browser.find_elements_by_tag_name, 'html')
        return new_page.text != self.old_page

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)


def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 15:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    print('WARNING: Time out exceeded')
    # raise Exception(
    #     'Timeout waiting for {}'.format(condition_function.__name__)
    # )

def materials():
    selector = find_element_safe(browser.find_elements_by_name, 'TabContainer1$TabPanel1$DataPageMaterial')
    return selector.find_elements_by_xpath("*")


def sources():
    selector = find_element_safe(browser.find_elements_by_name, 'TabContainer1$TabPanel1$DataPageSpecifics')
    return selector.find_elements_by_xpath("*")


def find_element_safe(func, arg, iteration=0):
    if iteration > 5:
        raise ValueError('Source selector not found.')

    elements = func(arg)
    if len(elements) > 0:
        return elements[0]
    else:
        time.sleep(0.1)
        return find_element_safe(func, arg, iteration + 1)

# endregion

# Load the page.
path_to_chromedriver = '/home/emher/Downloads/chromedriver'  # change path as needed
browser = webdriver.Chrome(executable_path=path_to_chromedriver)
url = 'https://www.pvlighthouse.com.au/resources/photovoltaic%20materials/refractive%20index/refractive%20index.aspx'
browser.get(url)

# Do the scraping.
limit = 1e6
k = 0
for i in range(27, len(materials())):
    # Select the element and WAIT.
    print('Clicking on {}'.format(materials()[i].text).encode('utf-8'))
    with wait_for_page_load(browser):
        materials()[i].click()
    print('Downloading data for {}'.format(materials()[i].text.encode('utf-8')))
    for j in range(0, len(sources())):
        # Don't click the first time; data are already loaded.
        if j is not 0:
            # Select source.
            print('Clicking on {}'.format(sources()[j].text.encode('utf-8')))
            with wait_for_page_load(browser):
                sources()[j].click()
        # Download data for the currently selected material.
        print('Downloading data from {}'.format(sources()[j].text.encode('utf-8')))
        export_btn = browser.find_element_by_id('btnExportToExcelFile')
        browser.execute_script('document.getElementById("btnExportToExcelFile").click();')
        # Rename the download so we know what's been downloaded.
        download_in_progress = True
        while download_in_progress:
            try:
                candidates = glob.iglob(os.path.join('/home/emher/Downloads/', 'PVL*.xls'))
                newest = max(candidates, key=os.path.getctime)
                base = os.path.basename(newest)
                name, ext = os.path.splitext(base)
                download_in_progress = False
            except ValueError:
                time.sleep(1e-3)
        os.rename(newest, newest.replace(name, '{}-{}'.format(materials()[i].text.encode('utf-8'), sources()[j].text.encode('utf-8'))))
        k += 1
        # Just take the first 5...
        if k > limit: break
    if k > limit: break