from selenium import webdriver
from selenium.webdriver import DesiredCapabilities


#depot = DepotManager.get()
#driver = webdriver.PhantomJS(desired_capabilities=desired_capabilities)
driver = webdriver.Firefox()
#driver.set_window_size(1024, 768) # set the window size that you need
#driver.maximize_window()
#driver.set_window_size(1366, 728) # optional
driver.get('https://github.com')

#driver.save_screenshot('github.png')

#result = driver.execute_script("return document.documentElement.outerHTML")

ids = driver.find_elements_by_xpath('//*')
for ii in ids:
    #print ii.tag_name
    print(ii.tag_name, ii.location, ii.size, ii.xpath )   # id name as string

# scroll down and take save_screenshot

# stich all the images

driver.close()
'''

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
options.binary_location = "/usr/local/bin"
driver = webdriver.Chrome(chrome_options=options)

driver.get('https://python.org')
driver.save_screenshot("screenshot.png")

driver.close()

'''
