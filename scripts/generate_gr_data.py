import pandas as pd
import numpy as np
import configparser as cp
import requests
from lxml import etree
import pygsheets

gc = pygsheets.authorize(service_file = '../configs/MyLibrary_creds.json')
sh = gc.open_by_key('1XThz9NPytkAqDzI1Cr8_-zdEGC4YCrOZO4r1UdOPDCc')

config_parser = cp.ConfigParser()
config_parser.read('../configs/secret.config')
gr_key = config_parser.get('DEFAULT', 'key')
sheets = ['test1','test2']

# Given partial row, returns (book_id, ratings_count, reviews_count, pub_year, avg_rating)
def get_book_info(row):
    query = "{} {} {}".format(row['Title'], row['Author First'], row['Author Last'])
    response = requests.get(
        'https://www.goodreads.com/search/index.xml',
        params = {'key':gr_key, 'q':query}
    )
    root = etree.fromstring(response.content)
    # root -> search -> results
    total_results = root[1][3]
    if int(total_results.text) == 0:
        # couldn't find any goodreads results, leaving empty
        return row
    results = root[1][6]
    work_node = results[0]
    if work_node[0].text is not None:
        row['gr_book_id'] = int(work_node[0].text)
    if work_node[2].text is not None:
        row['ratings_count'] = int(work_node[2].text)
    if work_node[3].text is not None:
        row['reviews_count'] = int(work_node[3].text)
    if work_node[4].text is not None:
        row['pub_year'] = int(work_node[4].text)
    if work_node[7].text is not None:
        row['avg_rating'] = float(work_node[7].text)
    return row

for ind, sheet_name in enumerate(sheets):
    input_sheet = sh.worksheet_by_title(sheet_name)
    df = input_sheet.get_as_df(has_header=True)
    df = df.apply(get_book_info, axis=1)
    output_name = '{} full'.format(sheet_name)
    found = False
    for wks in sh.worksheets():
        if wks.title == output_name:
            found = True
            break
    if not found:
        sh.add_worksheet(output_name)
    output_sheet = sh.worksheet_by_title(output_name)
    output_sheet.clear(start = 'A1')
    output_sheet.set_dataframe(df, start = 'A1', nan = '')
    # output_sheet.cell('A1').set_text_format('bold', True)
    # output_sheet.get_values(start = 'A1', end = 'A{}'.format(len(df.columns)),returnas = 'range').apply_format(output_sheet.cell('A1'))





