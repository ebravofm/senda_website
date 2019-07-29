from py.progress_tools import update_qualtrics_progress
from flask import Flask, render_template
import pandas as pd
import gpandas as gpd
import datetime
import numpy as np
from sms import sms_page

app = Flask(__name__)

app.register_blueprint(sms_page)

G = {'info': '1JV6tOulapdvDkT9RIEsf-rwUUefg9xHGYMuW4nFI_vM',
     'formularios': '1svbIKSKB5v0LjKUgEt0_cqQRU83d_7fzRyoywMKKAHI',
     'progress': '1My0exuCahxoaY78Aybw1NQQgA9C4DWFtEt34eQzVO5Q',
     'gsheets': '1b6KX9vshrT-2UiDHafNp1Hug2OFSSl1y_TCXg_xLZBw',
     'indirectos': '1w-YUnFu6F1dF6CZ2bfaahWJODlpDLKiiTDZdCy6o_iM'}

@app.route('/ias-uchile')
def index():
    csv = gpd.read_gexcel(G['info'])
    return render_template('index.html', csv = csv)


@app.route('/refresh-progress')
def refresh_progress():
    update_qualtrics_progress(json_path='static/data/progress.json')
    return 'Listo!'


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/ias-uchile/avance')
def avance():
    info = gpd.read_gexcel(G['info'])
    info = info[~info.Cod.str.contains('TEST')]

    formularios = gpd.gExcelFile(G['formularios'])

    forms = {}
    for centro in formularios.sheet_names:
        forms[centro] = formularios.parse(centro)
        forms[centro].dropna(inplace=True)

    return render_template('avance.html', info=info, forms=forms)


@app.route('/ias-uchile/avance/test')
def avance_test():
    info = gpd.read_gexcel(G['info'])

    formularios = gpd.gExcelFile(G['formularios'])

    forms = {}
    for centro in formularios.sheet_names:
        forms[centro] = formularios.parse(centro)
        forms[centro].dropna(inplace=True)

    return render_template('avance.html', info=info, forms=forms)


@app.route('/input/<cod>')
def input(cod):

    layout = gpd.read_gexcel(G['formularios'], sheet_name=cod.upper())
    layout.dropna(inplace=True)
    layout['tog'] = 'tog'+layout['Nombre Módulo'].str.replace(' ', '')

    return render_template('input.html', layout=layout)


@app.route('/ias-uchile/mapa')
def mapa():
    return render_template('mapa.html')


@app.route('/ias-uchile/results')
def results():
    info = gpd.read_gexcel(G['info'])
    info = info[~info.Cod.str.contains('TEST')]

    info['Tipo'] = info['Tipo'] + ' ' + info['Población']
    info = info[['Cod', 'Nombre', 'Tipo', 'Letra']]

    progress = gpd.read_gexcel(G['progress'])
    progress['Color'] = np.where(progress['Progress']==100, '#009efb', '#a6b7bf')
    progress['Title'] = np.where(progress['Progress']==100, 'Completo', 'Incompleto')
    progress = progress[['Centro', 'Icon', 'Progress', 'Color', 'Title']].set_index('Centro')
    color = pd.Series(['', 'round-success', 'round-primary', 'round-warning', 'round-danger']*5)
    
    gsheets = gpd.read_gexcel(G['gsheets']).set_index('COD')['ID']
    indirectos = gpd.read_gexcel(G['indirectos']).set_index('COD')['ID']
    
    return render_template('results.html', info=info, progress=progress, color=color, gsheets=gsheets, indirectos=indirectos)


@app.route('/ias-uchile/results/test')
def results_test():
    info = gpd.read_gexcel(G['info'])
    info['Tipo'] = info['Tipo'] + ' ' + info['Población']
    info = info[['Cod', 'Nombre', 'Tipo', 'Letra']]

    progress = gpd.read_gexcel(G['progress'])
    progress['Color'] = np.where(progress['Progress']==100, '#009efb', '#a6b7bf')
    progress['Title'] = np.where(progress['Progress']==100, 'Completo', 'Incompleto')
    progress = progress[['Centro', 'Icon', 'Progress', 'Color', 'Title']].set_index('Centro')
    color = pd.Series(['', 'round-success', 'round-primary', 'round-warning', 'round-danger']*5)
    
    gsheets = gpd.read_gexcel(G['gsheets']).set_index('COD')['ID']
    indirectos = gpd.read_gexcel(G['indirectos']).set_index('COD')['ID']
    
    return render_template('results.html', info=info, progress=progress, color=color, gsheets=gsheets, indirectos=indirectos)


if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=True)