import pandas as pd

try:
    from .selenium_tools import get_survey_responses
except:
    from selenium_tools import get_survey_responses
try:
    from .basic_tools import get_qualtrics_ids
except:
    from basic_tools import get_qualtrics_ids
try:
    from .progress_tools import update_progress
except:
    from progress_tools import update_progress

    '''
    TODO: Add IF len>3'''

    
def dump_responses(response_folder='../static/data/responses'):
    survey_ids = get_qualtrics_ids()

    progress = []

    for s in survey_ids:
        print(f'[·] {s[0]}...')
        try:
            response_table = get_survey_responses(s[1])
            response_table['COD'] = s[0]
            
            if len(response_table) > 2:

                response_table.to_csv(f'{response_folder}/{s[0]}_{s[1]}.tsv', sep='\t', encoding='utf-8-sig', index=False)
                print(f'[+] Succesfully dumped response {s[0]} {s[1]}')
                print()

                progress.append(get_progress_100(response_table))

            else:
                print(f'[-] Response table empty {s[0]} {s[1]}')
                print()

        except Exception as exc:
            print(f'[-] Could not dump response {s[0]} {s[1]}', exc)
            print()
            
    progress_100 = pd.concat(progress)
    
    update_progress(progress_100)


def get_progress_100(response_table):
    response_table = response_table[2:]
    centros = response_table['RecipientEmail'].tolist()
    COD = response_table['COD'].tolist()[0]
    
    df = pd.DataFrame({'COD': COD, 'Centro': centros, 'Progress': [100]*len(centros)})
    
    return df