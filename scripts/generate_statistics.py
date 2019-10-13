import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import numpy as np
import configparser as cp
import requests
from lxml import etree
import pygsheets
from collections import Counter
from tqdm import tqdm

config_parser = cp.ConfigParser()
config_parser.read('../configs/secret.config')
gr_key = config_parser.get('DEFAULT', 'key')
sheet_id = config_parser.get('DEFAULT', 'gsheet_id')
tqdm.pandas()

gc = pygsheets.authorize(service_file = '../configs/MyLibrary_creds.json')
sh = gc.open_by_key(sheet_id)

# sheets = ['Zuo collection full', 'van de Ven collection full']
sheets = ['test full', 'test2 full']
dfs = []

output_name = 'Analytics'
if not output_name in [x.title for x in sh.worksheets()]:
    sh.add_worksheet(output_name)
output_sheet = sh.worksheet_by_title(output_name)
output_sheet.clear(start = 'A1')

for ind, sheet_name in enumerate(sheets):
    input_sheet = sh.worksheet_by_title(sheet_name)
    dfs.append(input_sheet.get_as_df(has_header=True))
    output_sheet.update_value((1,2+ind*2), sheet_name)


# longest and shortest titles (rows 2-3)
output_sheet.update_value((2,1),'Shortest Title')
for ind, df in enumerate(dfs):
    title_length = df['Title'].map(len)
    output_sheet.update_value((2,ind*2+2),df.loc[title_length.argmin,'Title'])

output_sheet.update_value((3,1),'Longest Title')
for ind, df in enumerate(dfs):
    title_length = df['Title'].map(len)
    output_sheet.update_value((3,ind*2+2),df.loc[title_length.argmax,'Title'])

# most duplicate books (rows 4-6)
output_sheet.update_value((4,1),'Most Duplicate Books')
top_n_dups = 3
for ind, df in enumerate(dfs):
    book_freqs = df['Book ID'].value_counts()[:top_n_dups]
    row_num = 4
    for book_id, freq in book_freqs.items():
        output_sheet.update_value((row_num,ind*2+2),df.loc[df['Book ID'] == book_id].iloc[0]['Title'])
        output_sheet.update_value((row_num,ind*2+3),freq)
        row_num += 1


# most common author (rows 7-9)
output_sheet.update_value((4,1),'Most Common Authors')
top_n_authors = 3
for ind, df in enumerate(dfs):
    print('need to get the author ids...')


# most common keyword in titles (rows 10-12)


# genre distributions (rows 13-22)
output_sheet.update_value((13,1),'Most Popular Genres')
top_n_genres = 10
for ind, df in enumerate(dfs):
    all_genres = [x.split(',') for x in df['Genres'].tolist()]
    all_genres_flat = [item.strip() for sublist in all_genres for item in sublist]
    c = Counter(all_genres_flat)
    row_num = 13
    for genre, genre_count in c.most_common(top_n_genres):
        output_sheet.update_value((row_num,ind*2+2),genre)
        output_sheet.update_value((row_num,ind*2+3),genre_count)
        row_num += 1

