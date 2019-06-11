import pandas as pd
import os
from gspread_pandas import Spread, Client

def generate_gspread(template_id = '11MxWyub_4sxpAKmDceuN1WNgInku_T1Su4_duJ8mACo'):
    template_vais = '1jsPk9CDfY4Gf4Sroh4hrpLwf4MnmMyvVgVS0s7Ltqrc'
    template_osl = '11MxWyub_4sxpAKmDceuN1WNgInku_T1Su4_duJ8mACo'
    
    centros = ['CHIGUAYANTE', 'ESPERANZA', 'MELIPILLA', 'OBRERO', 'OSL', 'OSLBIOBIO', 'OSLLOSRIOS', 'OSLTARAPACA', 'OSLTEST', 'OSLVALPO', 'SEMILLAS', 'SIMBIOSIS', 'TEST']
    
    centros = [x for x in centros if 'OSL' in x]

    C = Client('ebravofm')

    d = {}
    for c in centros:
        S = C.copy(template_id, c, True)
        d[c] = S.id
        S.worksheets()[0].update_acell('B2', c)
        
    return d

    
def pop_X_gspread():
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
