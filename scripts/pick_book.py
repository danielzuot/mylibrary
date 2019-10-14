import pandas as pd
import numpy as np
import configparser as cp
import requests
from lxml import etree
import pygsheets
import argparse

def pick_book():
    config_parser = cp.ConfigParser()
    config_parser.read('../configs/secret.config')
    sheet_id = config_parser.get('DEFAULT', 'gsheet_id')

    gc = pygsheets.authorize(service_file = '../configs/MyLibrary_creds.json')
    sh = gc.open_by_key(sheet_id)

    parser = argparse.ArgumentParser(description='A tutorial of argparse!')
    parser.add_argument("--library", help='Whose library to pick the book from? (\'zuo\' or \'vandeven\')')
    parser.add_argument("--reader", help='Who will be reading the book? (\'zuo\',\'vandeven\', or \'both\')')
    parser.add_argument("--read", default = 0, help='Do you want a new book (0), one to reread (1), or to finish one already started (0.5)?')
    args = parser.parse_args()

    if args.library == 'zuo':
        sheet_name = 'Zuo collection full'
    elif args.library == 'vandeven':
        sheet_name = 'van de Ven collection full'
    else:
        print('Specified library not found.')
        return

    if args.reader == 'zuo':
        query_str = 'Has Daniel read? == {}'.format(args.read)
    elif args.reader == 'vandeven':
        query_str = 'Has Rebca read? == {}'.format(args.read)
    elif args.reader == 'both':
        query_str == 'Has Daniel read? == {} | Has Rebca read? == {}'.format(args.read, args.read)
    else:
        print('Specified reader not found.')
        return

    input_sheet = sh.worksheet_by_title(sheet_name)
    library_df = input_sheet.get_as_df(has_header=True, empty_value = np.nan)
    filtered_df = library_df.query(query_str)
    print(filtered_df.sample())


if __name__ == '__main__':
    pick_book()