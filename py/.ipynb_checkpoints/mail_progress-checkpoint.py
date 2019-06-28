import gpandas as gpd
import datetime
import os


try:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
except:
    pass


fecha = datetime.datetime.now().strftime("%d/%m")


def main():
    recipients = 'Emilio Bravo Maturana <ebravo@fen.uchile.cl>'
    titulo = f'Progreso al {fecha} (aviso automatizado)'
    html = populate_data_on_mail()
    
    send_mail(recipients, titulo, html)
    

def populate_data_on_mail():
    
    progress = gpd.read_gexcel('1My0exuCahxoaY78Aybw1NQQgA9C4DWFtEt34eQzVO5Q')[['Centro', 'Progress']].groupby(['Centro']).mean().round().astype(int)['Progress']
    progress_percent = (progress.astype(str) + '%').replace('0%','.')

    with open('mail_template.txt', 'r') as f:
        template = f.read()

    for centro in progress_percent.index:
        template = template.replace(f'#{centro}%#', str(progress_percent[centro]))
    for centro in progress.index:
        template = template.replace(f'#{centro}#', str(progress[centro]))
        
    return template


def send_mail(recipients, titulo, html):

    email = f'''From: Servidor SENDA <quimera.server@gmail.com>
To: {recipients}
Subject: {titulo}
Content-Type: text/html
<html>
    {html}
</html>
'''

    with open("progress_mail.txt", "w") as text_file:
        text_file.write(email)

    os.system('sendmail -t < progress_mail.txt')

    
if __name__ == "__main__":
    main()




