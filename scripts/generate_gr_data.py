import pandas as pd
import numpy as np
import configparser as cp
import requests
from lxml import etree
import pygsheets

config_parser = cp.ConfigParser()
config_parser.read('../configs/secret.config')
gr_key = config_parser.get('DEFAULT', 'key')
sheet_id = config_parser.get('DEFAULT', 'gsheet_id')

gc = pygsheets.authorize(service_file = '../configs/MyLibrary_creds.json')
sh = gc.open_by_key(sheet_id)

# sheets = ['Zuo collection','van de Ven collection']
sheets = ['test']

def find_best_book_match(results):
    # TODO: be smarter about finding better match
    return results[0]


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
    work_node = find_best_book_match(results)
    if work_node[0].text is not None:
        row['gr_work_id'] = int(work_node[0].text)
    if work_node[2].text is not None:
        row['ratings_count'] = int(work_node[2].text)
    if work_node[3].text is not None:
        row['reviews_count'] = int(work_node[3].text)
    if work_node[4].text is not None:
        row['pub_year'] = int(work_node[4].text)
    if work_node[7].text is not None:
        row['avg_rating'] = float(work_node[7].text)
    if work_node[8][0].text is not None:
        row['gr_book_id'] = work_node[8][0].text
    return row


def get_book_shelves(row):
    genreExceptions = {
        'to-read', 'currently-reading', 'owned', 'default', 'favorites', 'books-i-own',
        'ebook', 'kindle', 'library', 'audiobook', 'owned-books', 'audiobooks', 'my-books',
        'ebooks', 'to-buy', 'english', 'calibre', 'books', 'british', 'audio', 'my-library',
        'favourites', 're-read', 'general', 'e-books'
    }
    response = requests.get(
        'https://www.goodreads.com/book/show/{}'.format(row['gr_book_id']),
        params = {'key':gr_key, 'format':'xml'}
    )
    root = etree.fromstring(response.content)
    book = root[1]
    description = book[16]
    pop_shelves = book[28]
    shelves = []
    for shelf in pop_shelves:
        if shelf.get('name') not in genreExceptions:
            shelves.append(shelf.get('name'))
    row['genres'] = ", ".join(shelves)
    if description.text is not None:
        row['description'] = description.text
    return row


for ind, sheet_name in enumerate(sheets):
    input_sheet = sh.worksheet_by_title(sheet_name)
    df = input_sheet.get_as_df(has_header=True)
    df = df.apply(get_book_info, axis=1)
    df = df.apply(get_book_shelves, axis=1)
    print(df)
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





