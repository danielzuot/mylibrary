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

sheets = ['Zuo collection full', 'van de Ven collection full']
# sheets = ['test full', 'test2 full']
dfs = []

output_name = 'Analytics'
if not output_name in [x.title for x in sh.worksheets()]:
    sh.add_worksheet(output_name)
output_sheet = sh.worksheet_by_title(output_name)
output_sheet.clear(start = 'A1')
for i in range(10):
    output_sheet.update_value('A1', i)
current_row = 1
for ind, sheet_name in enumerate(sheets):
    input_sheet = sh.worksheet_by_title(sheet_name)
    dfs.append(input_sheet.get_as_df(has_header=True, empty_value = np.nan))
    output_sheet.update_value((current_row,2+ind*2), sheet_name)
current_row += 1

top_n_dups = 3
top_n_authors = 3
top_n_genres = 10
output_sheet.update_value((current_row,1),'Total Books')
current_row += 1
output_sheet.update_value((current_row,1),'Shortest Title')
current_row += 1
output_sheet.update_value((current_row,1),'Longest Title')
current_row += 1
output_sheet.update_value((current_row,1),'Oldest (by pub year)')
current_row += 1
output_sheet.update_value((current_row,1),'Newest (by pub year)')
current_row += 1
output_sheet.update_value((current_row,1),'Most popular (by rating count')
current_row += 1
output_sheet.update_value((current_row,1),'Highest rated')
current_row += 1
output_sheet.update_value((current_row,1),'Lowest rated')
current_row += 1
output_sheet.update_value((current_row,1),'Total finished by Daniel')
current_row += 1
output_sheet.update_value((current_row,1),'Total finished by Rebca')
current_row += 1
output_sheet.update_value((current_row,1),'Total only started by Daniel')
current_row += 1
output_sheet.update_value((current_row,1),'Total only started by Rebca')
current_row += 1
output_sheet.update_value((current_row,1),'Total unread by Daniel')
current_row += 1
output_sheet.update_value((current_row,1),'Total unread by Rebca')
current_row += 1
output_sheet.update_value((current_row,1),'Most Duplicate Books')
current_row += top_n_dups
output_sheet.update_value((current_row,1),'Most Common Authors')
current_row += top_n_authors
output_sheet.update_value((current_row,1),'Most Popular Genres')
current_row += top_n_genres
for ind, df in enumerate(dfs):
    current_row = 2
    output_sheet.update_value((current_row, ind*2 + 2), len(df))
    current_row += 1

    title_length = df['Title'].apply(str).map(len)
    output_sheet.update_value((current_row, ind*2 + 2), df.loc[title_length.argmin,'Title'])
    current_row += 1
    output_sheet.update_value((current_row, ind*2 + 2), df.loc[title_length.argmax,'Title'])
    current_row += 1

    oldest_year = int(df['Pub year'].min())
    output_sheet.update_value((current_row, ind*2 + 2), df.loc[df['Pub year'] == oldest_year]['Title'].iloc[0])
    output_sheet.update_value((current_row, ind*2 + 3), oldest_year)
    current_row += 1

    newest_year = int(df['Pub year'].max())
    output_sheet.update_value((current_row, ind*2 + 2), df.loc[df['Pub year'] == newest_year]['Title'].iloc[0])
    output_sheet.update_value((current_row, ind*2 + 3), newest_year)
    current_row += 1

    most_popular = int(df['Ratings count'].max())
    output_sheet.update_value((current_row, ind*2 + 2), df.loc[df['Ratings count'] == most_popular].iloc[0]['Title'])
    output_sheet.update_value((current_row, ind*2 + 3), most_popular)
    current_row += 1

    highest_rated = int(df['Avg rating'].max())
    output_sheet.update_value((current_row, ind*2 + 2), df.loc[df['Avg rating'] == highest_rated].iloc[0]['Title'])
    output_sheet.update_value((current_row, ind*2 + 3), highest_rated)
    current_row += 1

    lowest_rated = int(df['Avg rating'].min())
    output_sheet.update_value((current_row, ind*2 + 2), df.loc[df['Avg rating'] == lowest_rated].iloc[0]['Title'])
    output_sheet.update_value((current_row, ind*2 + 3), lowest_rated)
    current_row += 1

    daniel_read_freqs = df['Has Daniel read?'].value_counts()
    rebca_read_freqs = df['Has Rebca read?'].value_counts()
    output_sheet.update_value((current_row, ind*2 + 2), int(daniel_read_freqs.at[1.0]))
    current_row += 1
    output_sheet.update_value((current_row, ind*2 + 2), int(rebca_read_freqs.at[1.0]))
    current_row += 1
    output_sheet.update_value((current_row, ind*2 + 2), int(daniel_read_freqs.at[0.5]))
    current_row += 1
    output_sheet.update_value((current_row, ind*2 + 2), int(rebca_read_freqs.at[0.5]))
    current_row += 1
    output_sheet.update_value((current_row, ind*2 + 2), int(daniel_read_freqs.at[0.0]))
    current_row += 1
    output_sheet.update_value((current_row, ind*2 + 2), int(rebca_read_freqs.at[0.0]))
    current_row += 1

    book_freqs = df['Book ID'].value_counts().iloc[:top_n_dups]
    for book_id, freq in book_freqs.items():
        output_sheet.update_value((current_row, ind*2 + 2), df.loc[df['Book ID'] == book_id].iloc[0]['Title'])
        output_sheet.update_value((current_row, ind*2 + 3), freq)
        current_row += 1

    author_freqs = df['Author ID'].value_counts().iloc[:top_n_authors]
    for author_id, freq in author_freqs.items():
        first_author_row = df.loc[df['Author ID'] == author_id].iloc[0]
        output_sheet.update_value((current_row, ind*2 + 2), '{} {}'.format(first_author_row['Author First'], first_author_row['Author Last']))
        output_sheet.update_value((current_row, ind*2 + 3), freq)
        current_row += 1

    all_genres = [x.split(',') for x in df['Genres'].tolist() if pd.notnull(x)]
    all_genres_flat = [item.strip() for sublist in all_genres for item in sublist]
    c = Counter(all_genres_flat)
    for genre, genre_count in c.most_common(top_n_genres):
        output_sheet.update_value((current_row,ind*2+2),genre)
        output_sheet.update_value((current_row,ind*2+3),genre_count)
        current_row += 1


# most common keyword in titles (rows 10-12)



