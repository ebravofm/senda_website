import gpandas as gpd
import pandas as pd
pd.options.mode.chained_assignment = None

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

def get_qualtrics_ids():
    
    survey_df = get_survey_df()
    survey_df = survey_df[survey_df.Link.str.contains('qualtrics')].reset_index()
    survey_links = survey_df[['COD', 'Link']]
    survey_links['Link'] = survey_links.Link.apply(lambda x: x.split('/')[5].split('?')[0])
    survey_links = survey_links.drop_duplicates('Link')

    surveys = survey_links.values.tolist()
    
    return surveys
