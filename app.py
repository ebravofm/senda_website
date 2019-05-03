from flask import Flask, render_template
import pandas as pd


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/avance')
def avance():
    return render_template('avance.html')

@app.route('/mapa')
def mapa():
    return render_template('mapa.html')


@app.route('/tables')
def tables():
    csv = pd.read_csv('files/table.csv', sep=';')
    html_table = csv.to_html(index=False)
    html_table = html_table.replace(' border="1" ', ' ')
    html_table = html_table.replace('dataframe', 'table')


    return render_template('tables.html', html_table=html_table)


if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=True)