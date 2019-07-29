import pandas as pd
from xlrd import open_workbook
from xlutils.copy import copy
import os
from xlutils.styles import Styles

'''
TODO:
    #single value vs matrix
    #manage loops
    set blanks
    write format
'''

def main(template_xls):

    workbook = open_workbook(template_xls, formatting_info=True)
    
    dic_series = load_results_folder()
    
    for key in dic_series.keys():

        values = update_values(series=dic_series[key], workbook=workbook)
        blank_values = clean_workbook(workbook=workbook)
        fill_out_xls(blank_values+values, workbook, key)

    
def pop_matrix_questions(row):
    row_m = row[row.index.str.contains('M')]
    codes = list(set([prim_loop_code(x) for x in row_m.index]))

    for code in codes:
        row_m_i = row[row.index.str.contains(code) & row.index.str.contains('M')]

        if row_m_i.isnull().all():
            try:
                print(code)
                row[row.index.str.contains(code)] = row[code]
            except Exception as exc:
                print('Error filling matrix' + str(exc))
            
    return row


    
def load_results_folder():
    files = ['../results/'+fp for fp in os.listdir('../results') if 'tsv' in fp]

    d = {}
    for fp in files:
        df = pd.read_csv(fp, encoding='utf-16', sep='\t')
        df = df.iloc[2:].set_index('RecipientEmail')
        df = df[[col for col in df.columns if '#' in col]]

        for n, row in df.iterrows():
            row = pop_matrix_questions(row)
            d.setdefault(n,[]).append(row)

    for key in d.keys():
        d[key] = pd.concat(d[key]).dropna()
    
    return d
        
    
def get_coords(code, workbook):
    sheet_n = sheet_from_code(code)
    sheet_names = [sh for sh in workbook.sheet_names() if sh.split('.')[0] == sheet_n]
    
    for sheet_name in sheet_names:
        sheet = workbook.sheet_by_name(sheet_name)

        for i in range(sheet.nrows):
            row = sheet.row_values(i)

            for j in range(len(row)):
                if row[j] == code:
                    return [i, j, sheet_name]
                    break
                
    raise Exception(f'Code not found on sheet: "{code}".')

    
def update_values(series, workbook):
    '''
    TODO: single repeated record instead of matrix records
    '''    
    to_update = []
    for i, x in series.iteritems(): 
        try:
            coords = get_coords(i, workbook)
            to_update.append([x]+coords)
        except:
            pass
        
    return to_update

def clean_workbook(workbook):
    blank_values = []
    for sheet_name in workbook.sheet_names():
        sheet = workbook.sheet_by_name(sheet_name)

        for i in range(sheet.nrows):
            row = sheet.row_values(i)

            for j in range(len(row)):
                if '#' in row[j]:
                    blank_values.append(['', i, j, sheet_name])
    return blank_values

def fill_out_xls(values, workbook, name):
    '''
    values= [value, i, j, sheet]
    '''
    style = xlwt.easyxf('font: name Arial Narrow, height 220; align: horiz center; border: left thin,right thin,top thin,bottom thin')
    wb = copy(workbook)
    
    for val in values:
        sheet = wb.get_sheet(val[3])
        try:
            val[0] = int(val[0])
        except:
            pass
        sheet.write(val[1],val[2],val[0], style)
        
    wb.save(name + '.xls')


def sheet_from_code(code):
    c = [x for x, char in enumerate(code) if char == '#']
    return code[c[0]+1:c[1]].split('.')[0]

def prim_loop_code(full_code):
    c = [x for x, char in enumerate(full_code) if char == '#']
    return full_code[:c[1]+1]
