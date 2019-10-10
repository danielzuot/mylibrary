import pandas as pd
import numpy as np
import configparser as cp
import requests
from lxml import etree
import pygsheets

gc = pygsheets.authorize(service_file = '../configs/MyLibrary_creds.json')
sh = gc.open_by_key('1XThz9NPytkAqDzI1Cr8_-zdEGC4YCrOZO4r1UdOPDCc')

sheets = ['test1 full', 'test2 full']
dfs = []

for ind, sheet_name in enumerate(sheets):
    input_sheet = sh.worksheet_by_title(sheet_name)
    dfs.append(input_sheet.get_as_df(has_header=True))
output_name = '{} {} intersection'.format(sheets[0], sheets[1])
found = False
for wks in sh.worksheets():
    if wks.title == output_name:
        found = True
        break
if not found:
    sh.add_worksheet(output_name)
output_sheet = sh.worksheet_by_title(output_name)
output_sheet.clear(start = 'A1')
merged = pd.merge(dfs[0],dfs[1],how='inner',on=['gr_book_id'])
merged = merged[['gr_book_id','Author First_x','Author Last_x','Title_x','Additional Authors_x', 'Has Daniel read?_x','Has Rebca read?_x','ratings_count_x','reviews_count_x','pub_year_x','avg_rating_x']]
merged.columns = ['Goodreads book id', 'Author First', 'Author Last', 'Title', 'Additional Authors', 'Has Daniel read?', 'Has Rebca read?', 'Ratings #', 'Reviews #', 'Publication Year', 'Average Rating']
output_sheet.set_dataframe(merged, start = 'A1', nan = '')