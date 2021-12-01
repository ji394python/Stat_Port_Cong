from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from selenium.webdriver.common.keys import Keys
from datetime import datetime,timedelta
import os
from selenium.common.exceptions import ElementNotInteractableException
import traceback

#超參數設定
Account = input('輸入你的帳號')
Password = input('輸入你的密碼')
Port = input("輸入目標港口{'Los Angeles':'87','SHANGHAI':'1325'}")
Start = datetime.strptime(input('輸入開始日期：%Y-%m-%d'),'%Y-%m-%d')
End = datetime.strptime(input('輸入結束日期%Y-%m-%d'),'%Y-%m-%d')

Port = {'Los Angeles':'87','SHANGHAI':'1325'} #實際上港口走這
Days_diff = (End-Start).days + 1
colNames =   ['Vessel Name','Port Call Type', 'Port Type', 'Port At Call', 'Ata/atd11', 'Time At Port', 'In Transit Port Calls', 'Vessel Type - Detailed', 'Commercial Market']
groupTime = [0,5,14,50,1000]

#接受cookie與登入
options = webdriver.ChromeOptions()
options.add_argument('log-level=3')
print(os.getcwd(),os.listdir())
driver = webdriver.Chrome('./chromedriver.exe',options=options)
driver.get('https://www.marinetraffic.com/en/data/?asset_type=arrivals_departures')
element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='qc-cmp2-ui']/div[2]/div/button[2]"))
)
driver.find_element(By.XPATH, "//div[@id='qc-cmp2-ui']/div[2]/div/button[2]").click() # Cookie permission

#login
text =driver.find_elements_by_css_selector('.MuiButton-label')
for log in text:
    print(log.text)
    if log.text=="Log in":
        print(log.text)
        log.click()
time.sleep(3)
WebDriverWait(driver,30).until(lambda x: driver.find_element_by_css_selector('#email')).send_keys(Account)
WebDriverWait(driver,30).until(lambda x: driver.find_element_by_css_selector('#password')).send_keys(Password)
WebDriverWait(driver,30).until(lambda x: driver.find_element_by_css_selector('#login_form_submit')).click()
time.sleep(10) # Wait until page fully loaded (should be refactor)
def recur(s=0,ID='1325'):
            try:
                for h in groupTime[groupTime.index(s):]:
                    if h == 0:
                        #url設定
                        url_tail = 'https://www.marinetraffic.com/en/data/?asset_type=arrivals_departures'
                        url_col = '&columns=ata_atd:desc,shipname,move_type,port_type,port_name,time_at_port,intransit,specific_ship_type,market'
                        url_par = '&port_in|begins|%s|port_in=%s&ata_atd_between|range_date|ata_atd_between=%s,%s&move_type_in|in|Departure|move_type_in=1&time_at_port|range|time_at_port=%d,%d' %(portC,ID,date,date,h,groupTime[groupTime.index(h)+1])
                        Url = url_tail + url_col + url_par 
                        driver.get(Url)
                        
                        WebDriverWait(driver,30).until(lambda x: driver.find_element_by_css_selector('#reporting_ag_grid div .ag-header-cell'))
                        
                        
                        #帳號封包驗證程序
                        site = driver.page_source
                        soup = BeautifulSoup(site, 'html.parser')
                        length = len(soup.select('#reporting_ag_grid div .ag-header-cell')) 
                        while length <= 8:
                            driver.get(Url)
                            driver.refresh()
                            WebDriverWait(driver,30).until(lambda x: driver.find_element_by_css_selector('#reporting_ag_grid div .ag-header-cell'))
                            site = driver.page_source
                            soup = BeautifulSoup(site, 'html.parser')
                            length = len(soup.select('#reporting_ag_grid div .ag-header-cell'))
                            print('帳號憑證封包遺失 他媽的繼續重刷^_^')
                    elif h == 1000: 
                        globals()['s'] = 10
                        continue
                    else:
                        #Time At Port
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
                            if i.text == 'Time At Port': 
                                count_port += 1
                                if count_port == 2:
                                    i.click()
                                    break

                        
                        rangeFrom = driver.find_element_by_css_selector('label[for^=rangeFrom]')

                        rangeFrom.send_keys(Keys.CONTROL + "a");
                        rangeFrom.send_keys(Keys.DELETE);
                        rangeFrom.send_keys(h)

                        rangeTo = driver.find_element_by_css_selector('label[for^=rangeTo]')
                        rangeTo.send_keys(Keys.CONTROL + "a");
                        rangeTo.send_keys(Keys.DELETE);
                        rangeTo.send_keys(groupTime[groupTime.index(h)+1])
                        WebDriverWait(driver,30).until(lambda x: driver.find_elements_by_css_selector('.mt-filter-actions-inner > button[class^=btn]')[1]).click() 
                        time.sleep(3)
                        WebDriverWait(driver,30).until(lambda x: driver.find_element_by_css_selector('button[class^="btn filter-description flex-1-0-100 filter-pill-time_at_port"]')).click()
                        WebDriverWait(driver,30).until(lambda x: driver.find_element_by_css_selector('.filter-label:nth-of-type(2) button[class="btn filter-close"]')).click()
                        time.sleep(3)
                        pa = WebDriverWait(driver,30).until(lambda x: driver.find_element_by_css_selector('input[class^="MuiInputBase-input MuiInput-input MuiInputBase-inputMarginDense MuiInput-inputMarginDense"]'))
                        time.sleep(0.5)
                        pa.send_keys(Keys.CONTROL + "a");
                        pa.send_keys(1);
                        #帳號封包驗證程序
                        site = driver.page_source
                        soup = BeautifulSoup(site, 'html.parser')
                        
                    #爬取頁數確認
                    n_pages = 25 
                    n_true_pages = int(WebDriverWait(driver,30).until(lambda x: driver.find_elements_by_css_selector('.MuiTypography-body1')[-1].text[-2:]))
                    if n_true_pages <= n_pages:
                        n_pages = n_true_pages
                
                    #爬取表格資訊
                    for p in range(n_pages):
                        time.sleep(1)
                        site = driver.page_source
                        soup = BeautifulSoup(site, 'html.parser')
                        
                        if p != n_pages-1:
                            rows = 20
                        else:
                            rows = len(soup.select('#reporting_ag_grid div .ag-body-viewport > div > div[role^=row]'))
                        
                        content_cells = soup.select('#reporting_ag_grid div .ag-body-viewport > div > div[role^=row] > div[role^=gridcell]')
                        # content_pivlots = soup.select('#reporting_ag_grid div .ag-pinned-left-cols-viewport > div > div[role^=row]')
                        soup.select('#reporting_ag_grid div .MuiTablePagination-actions > button[aria-label^="Next page"]')
                        for col in range(rows):
                            # colDict[colNames[0]].append(content_pivlots[col].get_text())
                            for index in range(9):
                                colDict[colNames[index]].append(content_cells[index+col*9].get_text())
                        if p != n_pages-1:
                            next_page = "/html/body/main/div/div/div[3]/div[2]/div[1]/div/div/div/div/div[2]/div/section[2]/div/div/div/div[2]/div[3]/div/div/div/div/div[3]/button[2]"
                            driver.find_element(By.XPATH, next_page).click()

                    print('已完成爬取%s停留時間於(%d,%d) hours之間的港口資料,%s' %(date,h,groupTime[groupTime.index(h)+1],rows+20*(n_pages-1)))
            
            except:
            	traceback.print_exc()
            	return h
            
            s = h

#爬取程序
for portC in Port.keys():
    colDict = dict(zip(colNames,[ [] for i in range(len(colNames))]))
    for d in range(Days_diff):
        date = Start + timedelta(days=d)
        date = date.strftime('%Y-%m-%d')
        s = 0
        while (s != 1000) & (s is not None):
            s = recur(s,Port[portC])
        
        data = pd.DataFrame(colDict)

    data.to_csv(f'{portC}.csv',index=False,encoding='utf-8-sig') # Save data
    data.drop_duplicates(inplace=True)
    print('----%s港口爬取完成---' %portC)
