from gspread_pandas import Spread
import gpandas as gpd
import pandas as pd
import json
import numpy as np
try:
    from .selenium_tools import get_progress, get_survey_progress
except:
    from selenium_tools import get_progress, get_survey_progress
import warnings

pd.options.mode.chained_assignment = None


def update_progress(json_path='../static/data/progress.json'):
    warnings.filterwarnings("ignore")

    survey_df = get_survey_df()
    survey_df = pop_current_progress(survey_df)

    qualtrics = survey_df[survey_df.Link.str.contains('qualtrics')].reset_index()
    google = survey_df[survey_df.Link.str.contains('google')].reset_index()
    
    # Google
    

    # Qualtrics

    survey_links = qualtrics[['COD', 'Link']]
    survey_links['Link'] = survey_links.Link.apply(lambda x: x.split('/')[5].split('?')[0])
    survey_links = survey_links.drop_duplicates('Link')

    surveys = survey_links.values.tolist()

    progress_qualtrics = []
    for s in surveys:
        print(f'[·] {s[0]}...')
        print()
        table = get_survey_progress(s[0], s[1])
        try:
            table['COD'] = s[0]
            table = table[['COD', 'Email', 'Progress']]
            table.columns = ['COD', 'Centro', 'Progress']
            progress_qualtrics.append(table)
        except TypeError:
            print('[-] No table to append.')
            

    progress_qualtrics_df = pd.concat(progress_qualtrics)
    progress_qualtrics_df['Progress'] = progress_qualtrics_df['Progress'].apply(lambda x: int(str(x).replace('%', '')))

    # Merge

    result = pd.merge(survey_df, progress_qualtrics_df, 'left', on=['COD', 'Centro'])
    result['Progress'] = np.where(result.Progress_y.isnull(), result.Progress_x, result.Progress_y).astype(int)
    result = result.drop(['Progress_x', 'Progress_y'], axis=1)
    
    print()
    print(result[['COD', 'Centro', 'Progress']])
    print()
    
    # Update spreadsheet
    
    try:
        S = Spread(user = 'ebravofm', spread = '1My0exuCahxoaY78Aybw1NQQgA9C4DWFtEt34eQzVO5Q', user_creds_or_client=None)
        S.df_to_sheet(result, index=False, replace=True, sheet='progress')
        to_json(result, json_path)

        print('[+] PROGRESS TABLE UPDATED.')
    except exception as exc:
        print('[-] Could not update table.', exc)

    return survey_df


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


def get_survey_df():

    id_ = '1svbIKSKB5v0LjKUgEt0_cqQRU83d_7fzRyoywMKKAHI'
    forms = gpd.gExcelFile(id_)

    survey_df_ = []
    
    for sheet_name in forms.sheet_names:
        sheet = forms.parse(sheet_name)
        sheet['Centro'] = sheet_name
        sheet.dropna(inplace=True)

        survey_df_.append(sheet)

    survey_df = pd.concat(survey_df_)
    
    return survey_df


def pop_current_progress(df):
    
    df['Progress'] = 'N/A'
    historic = gpd.read_gexcel('1My0exuCahxoaY78Aybw1NQQgA9C4DWFtEt34eQzVO5Q', sheet_name='progress')[['Link', 'Progress']]
    historic.index = historic.Link
    historic = historic[['Progress']].dropna(how='any').to_dict()['Progress']
    for x in historic:
        df.loc[df.Link == x, 'Progress'] = historic[x]
    
    return df

    
    

