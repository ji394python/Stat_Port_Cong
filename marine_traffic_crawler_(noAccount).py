from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# html info for crawler
#
# port & vessel: class='ag-cell-content-link'
# time: class='ag-cell-content ag-cell-content-wrap'
# cookie accept button: xpath=//div[@id='qc-cmp2-ui']/div[2]/div/button[2]
# next page button: xpath=/html/body/main/div/div/div[3]/div[2]/div[1]/div/div/div/div/div[2]/div/section[2]/div/div/div/div[2]/div[3]/div/div/div/div/div[3]/button[2]


### bs4 filters

def object(tag, object):
    class_matched = False
    href_matched = False
    if tag.get('class') is not None:
        class_matched = ('ag-cell-content-link' in tag.get('class'))
    if tag.get('href') is not None:
        href_matched = (object in tag.get('href'))
    return  class_matched and href_matched

def vessel(tag):
    return object(tag, object='vessel')

def port(tag):
    return object(tag, object='port')

def time_(tag):
    class_matched = False
    if tag.has_attr('class'):
        class_matched = ("ag-cell-content", "ag-cell-content-wrap") == tuple(tag.get('class'))
    return class_matched

### Crawler

Port = input('輸入目標港口')

url = "https://www.marinetraffic.com/en/data/?asset_type=expected_arrivals&columns=shipname,recognized_next_port,reported_eta,arrived,show_on_live_map,dwt,ship_type"
driver = webdriver.Chrome()


driver.get(url)
element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='qc-cmp2-ui']/div[2]/div/button[2]"))
)
driver.find_element(By.XPATH, "//div[@id='qc-cmp2-ui']/div[2]/div/button[2]").click() # Cookie permission


time.sleep(10) # Wait until page fully loaded (should be refactor)


#Destination port
suggestion = WebDriverWait(driver,30).until(lambda x: driver.find_elements_by_css_selector('.IconDesc')) #find Add filter
count = 0
for sug in suggestion:
    if sug.text=="Add Filter":
        if count == 0 :
            count +=1 
        else:
            sug.click()
            break
            
portss = WebDriverWait(driver,30).until(lambda x: driver.find_elements_by_css_selector('.suggestion')) #find destination port
count_port = 0 
for i in portss:
    if i.text == 'Destination Port': 
        count_port += 1
        if count_port == 2:
            i.click()
            break

driver.find_element_by_css_selector('#autosuggest_').send_keys(Port)
WebDriverWait(driver,30).until(lambda x: driver.find_element_by_css_selector('.suggestion > div > span')).click() 

#Arrived Date
suggestion = WebDriverWait(driver,30).until(lambda x: driver.find_elements_by_css_selector('.IconDesc')) #find Add filter
count = 0
for sug in suggestion:
    if sug.text=="Add Filter":
        if count == 0 :
            count +=1 
        else:
            sug.click()
            break

arrive = WebDriverWait(driver,30).until(lambda x: driver.find_elements_by_css_selector('.suggestion'))
count_arri = 0 
for i in arrive:
    print(i.text)
    if i.text == 'Arrived At': 
        count_arri += 1
        if count_arri == 2:
            i.click()
            break
        
from selenium.webdriver.common.action_chains import ActionChains
slider = WebDriverWait(driver,30).until(lambda x: driver.find_element_by_css_selector('.container-slider')) #to arrive_at slider
ActionChains(driver).drag_and_drop_by_offset(slider, 110, 0).perform()
arri = WebDriverWait(driver,30).until(lambda x: driver.find_elements_by_css_selector('.btn'))
for ar in arri:
    if ar.text=="ADD FILTER":
        ar.click()
        break


site = driver.page_source
soup = BeautifulSoup(site, 'html.parser')
n_pages = 25 #int(soup.find_all('p', class_="MuiTypography-root MuiTypography-body1")[1].get_text()[3:])
n_true_pages = int(WebDriverWait(driver,30).until(lambda x: driver.find_elements_by_css_selector('.MuiTypography-body1')[-1].text[-2:]))
if n_true_pages <= n_pages:
    n_pages = n_true_pages

ports = []
vessels = []
reported_eta = []
arrived_at = []

for i in range(n_pages):
    print(f"Loading page {i} ...")
    site = driver.page_source
    soup = BeautifulSoup(site, 'html.parser')

    ports += [port.get_text() for port in soup.find_all(port)]
    vessels += [vessel.get_text() for vessel in soup.find_all(vessel)]
    reported_eta  += [ts.get_text() for ts in soup.find_all(time_)[0::2]]
    arrived_at += [ts.get_text() for ts in soup.find_all(time_)[1::2]]

    if i != n_pages-1:
        next_page = "/html/body/main/div/div/div[3]/div[2]/div[1]/div/div/div/div/div[2]/div/section[2]/div/div/div/div[2]/div[3]/div/div/div/div/div[3]/button[2]"
        driver.find_element(By.XPATH, next_page).click()

driver.close()

data = pd.DataFrame({   
    'Vessel Name': vessels, 
    'Destination Port': ports,
    'Reported Eta': reported_eta,
    'Arrived At': arrived_at
})

data.to_csv(f'{Port}.csv',index=False,encoding='utf-8-sig') # Save data
