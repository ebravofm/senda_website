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
    
    progress_df = check_qualtrics_progress()
    
    update_progress(progress_df, json_path)
    
    update_gspread_progress(progress_df)
    

def update_gspread_progress(progress_df):
    ids = {'CHIGUAYANTE': '1pn5X8TChQV1qXsPGX7VitlU63BBFUxbczGGkylmpwhw',
           'ESPERANZA': '1eC8n4MxN_kwy-ayTHrjFod_2yJ-31g4zcqzUYJ_vpuE',
           'MELIPILLA': '1Ita_p7BmqwwlrJJPhhjojLaZ9o4QFIc4s6z4626Irwc',
           'OBRERO': '1UCDGGGI7LOQqOD9E_M1ogFhVBRYzOms0qHFH9h2ujzk',
           'SEMILLAS': '15wWleuEs6E-VUGijWJtFHvQFcxbFVci_qt6SaPZ2E8c',
           'SIMBIOSIS': '1WG0WCobFB437yfZgCu1VzpCKH7vYSM4Kow_OFSRtm7U',
           'TEST': '1xwhFHBuQNFM0SLssEcMSuSuYfYJ-xzbX6ssrPWSBUZs',
           'OSLVALPO': '16erIoN3cxIot2tdnc72rQoq3kqfKwUNK97PFnRyRfOI',
           'OSLTEST': '1RA1eXMeVgUAB1VJkF5GGChHC0-_JRXOAOkOSWqAfww8',
           'OSLTARAPACA': '1mAGMSc2gol91qy2vgs2Xb0bs0rmMdkTTkhhVuAQFgmA',
           'OSLLOSRIOS': '1XTEsWupKGMd-nOcvgIPwA4xU5rf5BUgm1qWZ6h6XjUQ',
           'OSLBIOBIO': '1_RTp2FiuF9RDi7krpATiHuQSp9CFwz2p9P7zdOehKlU',
           'OSL': '14n9vCuAGW-_WOUAjWV9fHfdua8Ze9r5Av30veAdDDaM'}

    coords = {'RRHH': 'C8',
                  'USUARIOS-VAIS': 'C9',
                  'USUARIOS-OSL': 'C9',
                  'INFRAESTRUCTURA': 'C10',
                  'MOBILIARIO-VAIS': 'C11',
                  'MOBILIARIO-OSL': 'C11',
                  'BASICOS': 'C12',
                  'OTROS': 'C13',
                  'INDIRECTOS': 'C14'}
    
    print(progress_df)
    print(progress_df.Centro.unique())

    for centro in progress_df.Centro.unique():
        S = Spread(user = 'ebravofm', spread = ids[centro], user_creds_or_client=None)

        centro_df = progress_df[progress_df.Centro==centro]

        for n, row in centro_df.iterrows():
            S.sheets[0].update_acell(coords[row['COD']], row['Progress'])
    
    
def check_qualtrics_progress():
    
    survey_df = get_survey_df()
    survey_df = pop_current_progress(survey_df)

    qualtrics = survey_df[survey_df.Link.str.contains('qualtrics')].reset_index()
    google = survey_df[survey_df.Link.str.contains('google')].reset_index()
    
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


def pop_current_progress(df):
    
    df['Progress'] = 'N/A'
    historic = gpd.read_gexcel('1My0exuCahxoaY78Aybw1NQQgA9C4DWFtEt34eQzVO5Q', sheet_name='progress')[['Link', 'Progress']]
    historic.index = historic.Link
    historic = historic[['Progress']].dropna(how='any').to_dict()['Progress']
    for x in historic:
        df.loc[df.Link == x, 'Progress'] = historic[x]
    
    return df
