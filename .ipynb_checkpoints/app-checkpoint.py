from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    csv = pd.read_csv('files/table.csv').to_html()
    

    return render_template('index.html', csv=csv)

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=True)