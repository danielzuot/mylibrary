import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import numpy as np
import configparser as cp
import requests
from lxml import etree
import pygsheets
from tqdm import tqdm
from bs4 import BeautifulSoup

config_parser = cp.ConfigParser()
config_parser.read('../configs/secret.config')
gr_key = config_parser.get('DEFAULT', 'key')
sheet_id = config_parser.get('DEFAULT', 'gsheet_id')
tqdm.pandas()

gc = pygsheets.authorize(service_file = '../configs/MyLibrary_creds.json')
sh = gc.open_by_key(sheet_id)

sheets = ['Zuo collection','van de Ven collection']
# sheets = ['test','test2']
# sheets = ['van de Ven collection']

def find_best_book_match(results):
    # TODO: be smarter about finding better match
    return results.find('work')


def get_book_info(row):
    query = "{} {} {}".format(row['Title'], row['Author First'], row['Author Last'])
    response = requests.get(
        'https://www.goodreads.com/search/index.xml',
        params = {'key':gr_key, 'q':query}
    )
    soup = BeautifulSoup(response.content, 'xml')
    if int(soup.find('total-results').get_text()) == 0:
        # couldn't find any goodreads results, leaving empty
        return row
    results = soup.find('results')
    work_node = find_best_book_match(results)
    row['Work ID'] = work_node.id.get_text()
    row['Ratings count'] = work_node.ratings_count.get_text()
    row['Reviews count'] = work_node.text_reviews_count.get_text()

    row['Pub year'] = work_node.original_publication_year.get_text()
    row['Avg rating'] = work_node.average_rating.get_text()
    row['Book ID'] = work_node.best_book.id.get_text()
    row['Author ID'] = work_node.best_book.author.id.get_text()
    return row


def get_book_shelves(row):
    genreExceptions = {
        'to-read', 'currently-reading', 'owned', 'default', 'favorites', 'books-i-own',
        'ebook', 'kindle', 'library', 'audiobook', 'owned-books', 'audiobooks', 'my-books',
        'ebooks', 'to-buy', 'english', 'calibre', 'books', 'british', 'audio', 'my-library',
        'favourites', 're-read', 'general', 'e-books', 'to-reread', 'audio-books', 'german',
        'i-own', 'have', 'to-re-read', 'own-it', 'did-not-finish', 'on-my-shelf', 'wish-list',
        'personal-library', 'e-book', 'dnf', 'abandoned', 'hardcover', 'library-books', 'all-time-favorites', 'stand-alone', 'tbr', 'series', 'paperback', 'all'
    }
    max_shelves_per_book = 10
    if pd.isnull(row['Book ID']):
        return row
    response = requests.get(
        'https://www.goodreads.com/book/show/{}'.format(row['Book ID']),
        params = {'key':gr_key, 'format':'xml'}
    )
    soup = BeautifulSoup(response.content, 'xml')
    book = soup.find('book')
    description = book.description.get_text()
    sanitized_desc = BeautifulSoup(description, features='lxml').get_text()
    row['Description'] = sanitized_desc
    shelves = []
    for shelf in book.findAll("shelf"):
        if shelf.get('name') not in genreExceptions:
            shelves.append(shelf.get('name'))
        if len(shelves) == max_shelves_per_book:
            break
    row['Genres'] = ", ".join(shelves)
    return row


for ind, sheet_name in enumerate(sheets):
    input_sheet = sh.worksheet_by_title(sheet_name)
    df = input_sheet.get_as_df(has_header=True, empty_value = np.nan)
    df = df.progress_apply(get_book_info, axis=1)
    df = df.progress_apply(get_book_shelves, axis=1)
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
