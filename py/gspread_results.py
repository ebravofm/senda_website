import pandas as pd
import gpandas as gpd
import os
from gspread_pandas import Spread, Client


def generate_gspread():
    template_vais = '1jsPk9CDfY4Gf4Sroh4hrpLwf4MnmMyvVgVS0s7Ltqrc'
    template_osl = '11MxWyub_4sxpAKmDceuN1WNgInku_T1Su4_duJ8mACo'
    
    centros = ['CHIGUAYANTE', 'ESPERANZA', 'MELIPILLA', 'OBRERO', 'OSL', 'OSLBIOBIO', 'OSLLOSRIOS', 'OSLTARAPACA', 'OSLTEST', 'OSLVALPO', 'SEMILLAS', 'SIMBIOSIS', 'TEST']
    
    C = Client('ebravofm')

    d = {}
    for c in centros:
        if 'OSL' in c:
            S = C.copy(template_osl, c, True)
        else:
            S = C.copy(template_vais, c, True)
        d[c] = S.id
        S.worksheets()[0].update_acell('B2', c)
        
    return d

    
def pop_X_gspread():

    ids = gpd.read_gexcel('1b6KX9vshrT-2UiDHafNp1Hug2OFSSl1y_TCXg_xLZBw').set_index('COD')['ID']

    d = load_results_folder()

    for centro in d.keys():
        print(f'[·] Populating GSpread for {centro}')
        S = Spread(user = 'ebravofm', spread = ids[centro], user_creds_or_client=None)
        S.df_to_sheet(d[centro], index=True, replace=True, sheet='X')
        print('[+] Success!')



def load_results_folder(folder='../static/data/responses/'):
    files = [folder+fp for fp in os.listdir(folder) if 'tsv' in fp]

    d = {}
    for fp in files:

        #print(fp)
        df = pd.read_csv(fp, encoding='utf-8-sig', sep='\t')
        
        #Fix missing code #6.B#
        df.columns = [c.replace('Q28', '#6.B#') for c in df.columns]
        df.columns = [c.replace('Q33', '#2.D#') for c in df.columns]
        
        labels = df.iloc[0]
        labels = labels[[i for i in labels.index if '#' in i]]
        df = df.iloc[2:].set_index('RecipientEmail')
        df = df[[col for col in df.columns if '#' in col]]
        
        for n, row in df.iterrows():
            #print(n)
            row = pop_matrix_questions(row)
            full = pd.concat([row, labels], axis=1)
            full = full.fillna('-')
            d.setdefault(n,[]).append(full)

    for key in d.keys():
        d[key] = pd.concat(d[key])
    
    return d


def pop_matrix_questions(row):
    
    row_m = row[row.index.str.contains('M')]
    codes = list(set([prim_loop_code(x) for x in row_m.index]))

    for code in codes:
        row_m_i = row[row.index.str.contains(code) & row.index.str.contains('M')]

        if row_m_i.isnull().all():
            try:
                #print(code)
                row[row.index.str.contains(code)] = row[code]
            except Exception as exc:
                #print('Error filling matrix' + str(exc))
                pass
    
    return row



def prim_loop_code(full_code):
    c = [x for x, char in enumerate(full_code) if char == '#']
    return full_code[:c[1]+1]
