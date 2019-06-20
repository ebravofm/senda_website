import requests
from bs4 import BeautifulSoup as bs
import os
from selenium import webdriver
import sys
from pyvirtualdisplay import Display
import datetime

os.chdir(os.path.dirname(os.path.realpath(__file__)))


def browser(func):
    def browser_wrapper(*args, **kwargs):
        
        options = webdriver.ChromeOptions()

        if sys.platform == 'linux':
            display = Display(visible=0, size=(800, 600))
            display.start()
            options.add_argument(f"download.default_directory={os.getcwd()}")
            options.add_argument('--no-sandbox')

        d = webdriver.Chrome(options=options)

        
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

        return result
    
    return browser_wrapper

@browser
def get_progress_source(d):
    d.get('http://159.89.134.14/ias-uchile/avance')
    return d.page_source


def main():
    fecha = datetime.datetime.now().strftime("%d/%m")

    source = get_progress_source()
    soup = bs(source, 'lxml')
    avance_html = soup.find('div', attrs={'class': 'container-fluid'})

    avance = avance_html.prettify().replace('/input', 'http://159.89.134.14/input').replace('Detalles', '').replace('Avance', f'Avance al {fecha} <a href="http://159.89.134.14/ias-uchile/avance">(ver detalle)</a>').replace('m-t-15', '').replace('m-b-15', '')

    with open('css.txt', 'r') as f:
        css = f.read()

    html = f'''From: Servidor SENDA <quimera.server@gmail.com>
To: Emilio Bravo Maturana <ebravo@fen.uchile.cl>, Alberto José Muñoz Vergara <albmunoz@fen.uchile.cl>, Ana Maria Herrera <anitamherrera@hotmail.com>, Eduardo Andres Gallegos FEN <eandresgc@hotmail.com>, Magdalena Rendic <mrendicillanes@gmail.com>, "Pury Guzmán S." <puryguzmansalinas@gmail.com>
Subject: Progreso al {fecha} (aviso automatizado)
Content-Type: text/html

<html><style>{css}</style>{avance}</html>'''


    with open("progress_mail.txt", "w") as text_file:
        text_file.write(html)


    os.system('sendmail -t < progress_mail.txt')

if __name__ == "__main__":
    main()

    