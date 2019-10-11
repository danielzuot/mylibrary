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

# longest and shortest titles
# most duplicate books
# most common author
# most common keyword in titles
# genre distributions