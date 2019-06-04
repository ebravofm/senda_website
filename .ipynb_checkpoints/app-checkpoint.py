from py.update_progress import update_all
from flask import Flask, render_template
import pandas as pd
import gpandas as gpd
import datetime

app = Flask(__name__)

@app.route('/ias-uchile')
def index():
    csv = pd.read_csv('static/data/centros.csv', sep=';')
    return render_template('index.html', csv = csv)


@app.route('/refresh-progress')
def refresh_progress():
    update_all('static/data/progress.json')
    return 'Listo!'


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/ias-uchile/avance')
def avance():
    info = gpd.read_gexcel('1JV6tOulapdvDkT9RIEsf-rwUUefg9xHGYMuW4nFI_vM')
    formularios = gpd.gExcelFile('1svbIKSKB5v0LjKUgEt0_cqQRU83d_7fzRyoywMKKAHI')

    forms = {}
    for centro in formularios.sheet_names:
        forms[centro] = formularios.parse(centro)
        forms[centro].dropna(inplace=True)

    return render_template('avance.html', info=info, forms=forms)

@app.route('/input/<cod>')
def input(cod):

    layout = gpd.read_gexcel('1svbIKSKB5v0LjKUgEt0_cqQRU83d_7fzRyoywMKKAHI', sheet_name=cod.upper())
    layout.dropna(inplace=True)
    layout['tog'] = 'tog'+layout['Nombre Módulo'].str.replace(' ', '')

    return render_template('input.html', layout=layout)

@app.route('/ias-uchile/mapa')
def mapa():
    return render_template('mapa.html')

@app.route('/ias-uchile/formularios')
def formularios():
    return render_template('formularios.html')

@app.route('/ias-uchile/results')
def results():
    csv = pd.read_csv('files/table.csv', sep=';')
    html_table = csv.to_html(index=False)
    html_table = html_table.replace(' border="1" ', ' ')
    html_table = html_table.replace('dataframe', 'table')

    return render_template('results.html', html_table=html_table)


if __name__ == '__main__':
    app.run(port=5001, debug=True, use_reloader=True)