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


def browser(func):
    def browser_wrapper(*args, **kwargs):
        
        options = webdriver.ChromeOptions()

        if sys.platform == 'linux':
            display = Display(visible=0, size=(800, 600))
            display.start()
            options.add_argument(f"download.default_directory={os.getcwd()}")
            options.add_argument('--no-sandbox')

        d = webdriver.Chrome(options=options)

        d.get('https://login.qualtrics.com/login?lang=es-la')

        login(d)
        
        print('[+] Logged in.')

        try:
            result = func(d, *args, **kwargs)
            
        except Exception as exc:
            d.close()
            if sys.platform == 'linux':
                display.stop()
            raise RuntimeError(str(exc))


        d.close()
        if sys.platform == 'linux':
            display.stop()
        print('[+] Logged Out.')
        print()

        return result
    
    return browser_wrapper


@browser
def get_table_from_id(d, validate_value, survey_id):
    n = 0

    while n<5:
        try:
            # Go to URL
            d.get(f'https://fenuchile.ca1.qualtrics.com/responses/#/surveys/{survey_id}')
            
            wait = WebDriverWait(d, 2)
            
            # Wait and click for progress button
            in_progress = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-key="RESPONSES_IN_PROGRESS"]')))
            in_progress.click()

            n = 5

        except Exception as exc:
            #print(f'[-] Error. Reintentando... (url: {d.current_url})')
            n += 1

    sleep(3)
    
    # Looking for table
    try:
        table = d.find_element_by_tag_name('table')
        table_html = table.find_element_by_xpath('./..').get_attribute('innerHTML')
        df = pd.read_html(table_html)
        
    except NoSuchElementException:
        print('[-] Table does not exist.')
        return None
        
    # Processing Table.
    try:
        df = df[0]
        df.columns = [x.strip() for x in df.columns]
        
        if validate_value in df['Email'].tolist():
            print(f'[+] {validate_value} Table Found!')
            
            return df
            
        else:
            print('[-] Found Table but could not validate')
    except Exception as exc:
        print(f'[-] Error while processing table. {exc}')


@browser
def get_progress(d, survey_df):
    
    progress_dict = {}
    
    for n, survey in survey_df.iterrows():
        print()

        survey_id = survey['Link'].strip()

        survey_id_ = survey_id
        if 'fenuchile' in survey_id :
            survey_id = survey_id.split('/')[survey_id.split('/').index('form')+1].split('?')[0]
        try:
            print(f'[·] Looking Progress Table {survey["Centro"]}, {survey["Nombre Módulo"]}...')

            n = 0

            while n<5:
                try:
                    d.get(f'https://fenuchile.ca1.qualtrics.com/responses/#/surveys/{survey_id}')
                    wait = WebDriverWait(d, 2)
                    in_progress = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-key="RESPONSES_IN_PROGRESS"]')))
                    in_progress.click()

                    n = 5

                except Exception as exc:
                    print(f'[-] Error. Reintentando... (url: {d.current_url})')
                    n += 1

            sleep(3)
            table = d.find_element_by_tag_name('table')
            table_html = table.find_element_by_xpath('./..').get_attribute('innerHTML')
            df = pd.read_html(table_html)

            if not df:
                print('[-] Scraped empty table :()')
            else:
                print('[+] Table Found')

            try:
                df = df[0]
                df.columns = [col.strip() for col in df.columns]
                progress = df[df.Email=='X']['Progress'][0]
                print(f'[+] Progress: {survey["Centro"]}, {survey["Nombre Módulo"]}: {progress}')
                
            except Exception as exc:
                print('[-] Table has no progress')
                progress = '0%'
        except NoSuchElementException:
            print('[-] Table does not exist.')        
            progress = '0%'
        
        progress_dict[survey_id_] = progress   
            
    return progress_dict


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


def login(d):
    user = d.find_element_by_id('UserName')
    user.send_keys('ebravo@fen.uchile.cl')
    sleep(.5)
    pw = d.find_element_by_id('UserPassword')
    pw.send_keys('macro1213')
    sleep(.5)
    login = d.find_element_by_id('loginButton')
    login.click()