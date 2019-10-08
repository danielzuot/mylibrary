import pandas as pd
import numpy as np

lib1_path = './data/daniel_library.tsv'
# lib2_path = ''

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
print(lib1_df)
