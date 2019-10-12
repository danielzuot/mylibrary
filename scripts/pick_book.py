import pandas as pd
import numpy as np
import configparser as cp
import requests
from lxml import etree
import pygsheets
import argparse

config_parser = cp.ConfigParser()
config_parser.read('../configs/secret.config')
sheet_id = config_parser.get('DEFAULT', 'gsheet_id')

gc = pygsheets.authorize(service_file = '../configs/MyLibrary_creds.json')
sh = gc.open_by_key(sheet_id)

parser = argparse.ArgumentParser(description='A tutorial of argparse!')
parser.add_argument("--library", help='Whose library to pick the book from? (\'zuo\' or \'vandeven\')')
parser.add_argument("--reader", help='Who would be reading the book? (\'zuo\',\'vandeven\', or \'both\')')
parser.add_argument("--read", default = 0, help='Do you want a new book or one to reread? (0 or 1)')
args = parser.parse_args()


if args.library == 'zuo':
    sheet_name = 'Zuo collection full'
elif args.library == 'vandeven':
    sheet_name = 'van de Ven collection full'
else:
    print('Specified library not found.')

