import pandas as pd
import numpy as np
import configparser as cp
import requests
from lxml import etree
import pygsheets

config_parser = cp.ConfigParser()
config_parser.read('../configs/secret.config')
sheet_id = config_parser.get('DEFAULT', 'gsheet_id')

gc = pygsheets.authorize(service_file = '../configs/MyLibrary_creds.json')
sh = gc.open_by_key(sheet_id)

# sheets = ['Zuo collection full', 'van de Ven collection full']
sheets = ['test full', 'test2 full']
dfs = []

for ind, sheet_name in enumerate(sheets):
    input_sheet = sh.worksheet_by_title(sheet_name)
    dfs.append(input_sheet.get_as_df(has_header=True))
output_name = '{} {} intersection'.format(sheets[0], sheets[1])
if not output_name in [x.title for x in sh.worksheets()]:
    sh.add_worksheet(output_name)
output_sheet = sh.worksheet_by_title(output_name)
output_sheet.clear(start = 'A1')
intersection = pd.merge(dfs[0],dfs[1][pd.notnull(dfs[1]['Book ID'])],how='inner',on=['Book ID'])
new = dfs[0]['Book ID'].isin(intersection['Book ID'])
merged = dfs[0][new]
output_sheet.set_dataframe(merged, start = 'A1', nan = '')