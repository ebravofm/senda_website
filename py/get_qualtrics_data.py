from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from time import sleep
import pandas as pd
import requests
import zipfile
import sys
import os
import io

def zip2df(virtual_zip):
    open_zip = zipfile.ZipFile(io.BytesIO(virtual_zip))
    
    for file_name in open_zip.namelist():
        csv_file = open_zip.read(file_name)
        
    df = pd.read_csv(io.BytesIO(csv_file))
    
    return df
    
def request_zip(link, webdriver_cookies):
    
    cookies = {}
    for c in webdriver_cookies:
        cookies[c['name']]=c['value']

    virtual_zip = requests.get(link, cookies=cookies).content
    
    return virtual_zip


def get_survey(survey_id='SV_3xSvA9utuIDlR2J'):
    options = webdriver.ChromeOptions()
    
    if sys.platform == 'linux':
        display = Display(visible=0, size=(800, 600))
        display.start()

        options.add_argument(f"download.default_directory={os.getcwd()}")
        options.add_argument('--no-sandbox')

    d = webdriver.Chrome(options=options)

    try:
        d.get('https://login.qualtrics.com/login?lang=es-la')

        '''cookies = pd.read_pickle('qualtrics.ck')
        for cookie in cookies:
                d.add_cookie(cookie)'''
        login(d)
        
        print('[+] Logged in.')
        print('[·] Looking for Download Button...')

        n = 0
        while n<5:
            try:
                d.get(f'https://fenuchile.ca1.qualtrics.com/responses/#/surveys/{survey_id}')
                wait = WebDriverWait(d, 2)
                export_import = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-key="EXPORT_AND_IMPORT"]')))
                export_import.click()
                
                n = 5

            except Exception as exc:
                print(f'[-] Error. Reintentando... (url: {d.current_url})')
                n += 1
            
        sleep(2)

        export_data = d.find_element_by_xpath('//i[@class="icon icon-download-lg"]')
        export_data.click()
        sleep(2)

        download = d.find_element_by_xpath('//span[@data-key="DOWNLOAD"]')
        download.click()
        sleep(2)

        wait = WebDriverWait(d, 25)
        download2 = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-key="DOWNLOAD"]')))
        zip_link = download2.find_element_by_xpath('./..').get_property('href')
        zip_data = request_zip(zip_link, d.get_cookies())
        df = zip2df(zip_data)
    
        print('[+] Successfully scraped csv.')
        

        print('[·] Logging Out.')
        check = True
        while check:
            try:
                X = d.find_element_by_xpath('//span[@ng-click="deleteExportJob(export, $index)"]')
                X.click()
                sleep(1)
            except NoSuchElementException:
                check = False

    except Exception as exc:
        print(str(exc))
        print('[-] Error')
        d.close()
        if sys.platform == 'linux':
            display.stop()
        raise RuntimeError
    
    d.close()
    if sys.platform == 'linux':
        display.stop()
    print('[+] Logged Out.')
    
    return df
    
def login(d):
    user = d.find_element_by_id('UserName')
    user.send_keys('ebravo@fen.uchile.cl')
    sleep(.5)
    pw = d.find_element_by_id('UserPassword')
    pw.send_keys('macro1213')
    sleep(.5)
    login = d.find_element_by_id('loginButton')
    login.click()