from gspread_pandas import Spread
import gpandas as gpd
import pandas as pd
import json
import numpy as np
try:
    from .selenium_tools import get_survey_progress
except:
    from selenium_tools import get_survey_progress
try:
    from .basic_tools import get_survey_df
except:
    from basic_tools import get_survey_df

    
    
def update_qualtrics_progress(json_path='../static/data/progress.json'):
    
    progress_df = check_progress()
    
    update_progress(progress_df, json_path)
    
    update_gspread_progress(progress_df)
    

def update_gspread_progress(progress_df):
    ids = gpd.read_gexcel('1b6KX9vshrT-2UiDHafNp1Hug2OFSSl1y_TCXg_xLZBw').set_index('COD')['ID']

    coords = {'RRHH': 'C8',
                  'USUARIOS-VAIS': 'C9',
                  'USUARIOS-OSL': 'C9',
                  'INFRAESTRUCTURA': 'C10',
                  'MOBILIARIO-VAIS': 'C11',
                  'MOBILIARIO-OSL': 'C11',
                  'BASICOS': 'C12',
                  'OTROS': 'C13',
                  'INDIRECTOS': 'C14'}
    
    centros = [c for c in progress_df.Centro.unique() if c not in ['RRHH', 'USUARIOS-VAIS', 'INFRAESTRUCTURA','MOBILIARIO-VAIS', 'BASICOS', 'OTROS', 'USUARIOS-OSL', 'MOBILIARIO-OSL']]

    for centro in centros:
        print(f'[·] Processing {centro} GSpread...')
        S = Spread(user = 'ebravofm', spread = ids[centro], user_creds_or_client=None)

        centro_df = progress_df[progress_df.Centro==centro]

        for n, row in centro_df.iterrows():
            try:
                #print(f'[·] {row['COD']}...')
                S.sheets[0].update_acell(coords[row['COD']], row['Progress'])
            except KeyError:
                pass

    print('[+] Success.')
    
    
def google_progress(google):
    
    for link in google['Link'].unique():
        #print(link)
        indirectos = gpd.read_gexcel(link).iloc[:,-1].fillna('')
        i = indirectos[indirectos == 'MONTO TOTAL ANUAL'].index[0]
        values = indirectos[i+1:]
        empty_count = values.value_counts()['']
        percent = round(((len(values)-empty_count)/len(values))*100)
        #print(percent)
        
        google['Progress'] = np.where(google.Link==link, percent, google.Progress).astype(int)

    google = google[['COD', 'Centro', 'Progress']]
        
    return google

def qualtrics_progress(qualtrics):
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
        print()
            
    progress_qualtrics_df = pd.concat(progress_qualtrics)
    progress_qualtrics_df['Progress'] = progress_qualtrics_df['Progress'].apply(lambda x: int(str(x).replace('%', '')))
    
    return progress_qualtrics_df
    
def check_progress():
    
    survey_df = get_survey_df()
    survey_df = pop_current_progress(survey_df)

    qualtrics_input = survey_df[survey_df.Link.str.contains('qualtrics')].reset_index()
    google_input = survey_df[survey_df.Link.str.contains('google')].reset_index()
    
    # Google
    google = google_progress(google_input)
    
    # Qualtrics
    qualtrics = qualtrics_progress(qualtrics_input)
    
    
    progress_df = pd.concat([qualtrics, google])
    
    return progress_df


def update_progress(progress_df, json_path='../static/data/progress.json'):

    survey_df = get_survey_df()
    survey_df = pop_current_progress(survey_df)

    # Merge

    result = pd.merge(survey_df, progress_df, 'left', on=['COD', 'Centro'])
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


def pop_current_progress(df):
    
    df['Progress'] = 'N/A'
    historic = gpd.read_gexcel('1My0exuCahxoaY78Aybw1NQQgA9C4DWFtEt34eQzVO5Q', sheet_name='progress')[['Link', 'Progress']]
    historic.index = historic.Link
    historic = historic[['Progress']].dropna(how='any').to_dict()['Progress']
    for x in historic:
        df.loc[df.Link == x, 'Progress'] = historic[x]
    
    return df


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