from .get_qualtrics_data import get_progress
from gspread_pandas import Spread
import gpandas as gpd
import pandas as pd
import json

pd.options.mode.chained_assignment = None


def update_all():
    
    full = get_full_form()
    full = get_historic_progress(full)

    qualtrics = full[full.Link.str.contains('qualtrics')].reset_index()
    google = full[full.Link.str.contains('google')].reset_index()
    
    # Qualtrics
    to_get_qualtrics = list(set(qualtrics['Link'].tolist()))
    p = get_progress(to_get_qualtrics)

    for x in p:
        full.loc[full.Link == x, 'Progress'] = p[x]
        
    # Update spreadsheet
    S = Spread('ebravofm', '1My0exuCahxoaY78Aybw1NQQgA9C4DWFtEt34eQzVO5Q')
    S.df_to_sheet(full, index=False, replace=True, sheet='progress')
    to_json(full)
    
    
    return full
    
def to_json(df):
    
    df = df[['Centro', 'Nombre Módulo', 'Progress']]
    drec = dict()
    ncols = df.values.shape[1]
    for line in df.values:
        d = drec
        for j, col in enumerate(line[:-1]):
            if not col in d.keys():
                if j != ncols-2:
                    d[col] = {}
                    d = d[col]
                else:
                    d[col] = line[-1]
            else:
                if j!= ncols-2:
                    d = d[col]
    
    with open('../data/progress.json', 'w') as fp:
        json.dump(drec, fp)
    
    return drec

def get_full_form():

    id_ = '1svbIKSKB5v0LjKUgEt0_cqQRU83d_7fzRyoywMKKAHI'
    forms = gpd.gExcelFile(id_)

    full_ = []
    
    for sheet_name in forms.sheet_names:
        sheet = forms.parse(sheet_name)
        sheet['Centro'] = sheet_name
        sheet.dropna(inplace=True)

        full_.append(sheet)

    full = pd.concat(full_)
    
    return full


def get_historic_progress(df):
    
    df['Progress'] = 'N/A'
    historic = gpd.read_gexcel('1My0exuCahxoaY78Aybw1NQQgA9C4DWFtEt34eQzVO5Q', sheet_name='progress')[['Link', 'Progress']]
    historic.index = historic.Link
    historic = historic[['Progress']].dropna(how='any').to_dict()['Progress']
    for x in historic:
        df.loc[df.Link == x, 'Progress'] = historic[x]
    
    return df

    
    

