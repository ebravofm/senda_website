from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    csv = pd.read_csv('files/table.csv')
    html_table = csv.to_html()
    html_table = html_table.replace(' border="1" ', ' ')
    html_table = html_table.replace('dataframe', 'table')


    return render_template('index.html', html_table=html_table)

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=True)