from gspread_pandas import Spread
import gpandas as gpd
import pandas as pd
import json
import numpy as np
try:
    from .get_qualtrics_data import get_progress, get_table_from_id
except:
    from get_qualtrics_data import get_progress, get_table_from_id

pd.options.mode.chained_assignment = None


def update_all(json_path='../static/data/progress.json'):

    full = get_full_form()
    full = get_historic_progress(full)

    qualtrics = full[full.Link.str.contains('qualtrics')].reset_index()
    google = full[full.Link.str.contains('google')].reset_index()

    # Qualtrics

    survey = qualtrics[['COD', 'Link']]
    survey['Link'] = survey.Link.apply(lambda x: x.split('/')[5].split('?')[0])
    survey = survey.drop_duplicates('Link')

    surveys = survey.values.tolist()

    progress = []
    for s in surveys:
        print()
        print(f'[·] {s[0]}...')
        table = get_table_from_id(s[0], s[1])
        try:
            table['COD'] = s[0]
            table = table[['COD', 'Email', 'Progress']]
            table.columns = ['COD', 'Centro', 'Progress']
            progress.append(table)
        except TypeError:
            print('[-] No table to append.')

    progress_df = pd.concat(progress)
    progress_df['Progress'] = progress_df['Progress'].apply(lambda x: int(str(x).replace('%', '')))


    result = pd.merge(full, progress_df, 'left', on=['COD', 'Centro'])
    result['Progress'] = np.where(result.Progress_y.isnull(), result.Progress_x, result.Progress_y)
    result = result.drop(['Progress_x', 'Progress_y'], axis=1)

    # Update spreadsheet
    S = Spread('ebravofm', '1My0exuCahxoaY78Aybw1NQQgA9C4DWFtEt34eQzVO5Q')
    S.df_to_sheet(result, index=False, replace=True, sheet='progress')
    to_json(result, json_path)

    return full


def to_json(df, json_path='../static/data/progress.json'):
    
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
    
    with open(json_path, 'w') as fp:
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

    
    

