from selenium import webdriver

driver = webdriver.PhantomJS()
# driver.set_window_size(1120, 550)
# driver.get("http://www.film2movie.biz")
driver.get("http://linarch.ir/")
driver.find_element_by_class_name("line")
print(driver.current_url)
# driver.find_element_by_id('search_form_input_homepage').send_keys("realpython")
# driver.find_element_by_id("search_button_homepage").click()
# print(driver.current_url)
driver.quit()
