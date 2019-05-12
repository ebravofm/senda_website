from selenium import webdriver

def browser(func):
    def browser_wrapper(*args, **kw):
        driver = webdriver.Chrome()
        title = func(driver, *args, **kw)
        driver.close()
        
        return title
    
    return browser_wrapper

@browser
def task(driver, url):
    driver.get(url)
    return driver.title