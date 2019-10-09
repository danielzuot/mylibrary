import pandas as pd
import numpy as np
import configparser as cp
import requests
from lxml import etree

lib1_path = '../data/daniel_library.tsv'
# lib2_path = '../data/rebca_library.tsv'

config_parser = cp.ConfigParser()
config_parser.read('./secret.config')
gr_key = config_parser.get('DEFAULT', 'key')

lib1_df = pd.read_csv(
                lib1_path,
                sep='\t',
                names=[ 'author_first',
                        'author_last',
                        'title',
                        'additional_authors',
                        'location',
                        'daniel_read',
                        'rebca_read'],
                skiprows=2
            )

# Returns (book_id, ratings_count, reviews_count, pub_year, avg_rating)
def get_book_info(row):
    query = "{} {} {}".format(row['title'], row['author_first'], row['author_last'])
    response = requests.get(
        'https://www.goodreads.com/search/index.xml',
        params = {'key':gr_key, 'q':query}
    )
    root = etree.fromstring(response.content)
    # root -> search -> results
    results = root[1][6]
    if len(results):
        # found at least one match
        work_node = results[0]
        return (work_node[0].text, work_node[2].text, work_node[3].text, work_node[4].text, work_node[7].text)
    else:
        return ('NAN', 'NAN', 'NAN', 'NAN', 'NAN')

    
# lib2_df = pd.read_csv(
#                 lib2_path,
#                 sep='\t',
#                 names=[ 'author_first',
#                         'author_last',
#                         'title',
#                         'additional_authors',
#                         'location',
#                         'daniel_read',
#                         'rebca_read'],
#                 skiprows=2
#             )

lib1_df['gr_book_id'], lib1_df['ratings_count'], lib1_df['reviews_count'], lib1_df['pub_year'], lib1_df['avg_rating'] = lib1_df.apply(get_book_info, axis=1)
print(lib1_df)


