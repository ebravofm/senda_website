from get_qualtrics_data import get_progress
import gpandas as gpd
import pandas as pd

pd.options.mode.chained_assignment = None

form_links_id = '1svbIKSKB5v0LjKUgEt0_cqQRU83d_7fzRyoywMKKAHI'
forms = gpd.gExcelFile(form_links_id)

full_ = []
for sheet_name in forms.sheet_names:
    sheet = forms.parse(sheet_name)
    sheet['Centro'] = sheet_name
    sheet.dropna(inplace=True)
    
    full_.append(sheet)
    
full = pd.concat(full_).reset_index()
full['Progress'] = 'N/A'

to_get = list(set(full['Link'].tolist()))

p = get_progress(to_get)

for x in p:
    full.loc[full.Link == x, 'Progress'] = p[x]

