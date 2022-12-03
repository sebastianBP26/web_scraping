# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 12:18:20 2022

@author: Sebastian Barroso
"""

import time

# Pre - install
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

# This is an example of web scraping using a statical website.

# ***** This script helps us to get data from a website which calls "Eusica". ***** 
# ***** This is only for education purposes and for own use. ***** 
# ***** Not for commercial use. ***** 

# Page that we want to scraper
main_url = 'https://eusica.mx/productos/guitarras/guitarras_el%C3%A9ctricas/'

# Headers for request
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}

# Number of pages that we want to scraper
pages_to_scrape = 37

# Function to get the data
def get_data_page(url):
    
    # Click on the page (url)
    html = requests.get(url, headers = headers) 
   
    # Making the soup.
    bs = BeautifulSoup(html.content, 'html.parser') 
    
    # We get all the links in the page
    links = bs.find_all('a', class_ = 'product-title') 
    
    # Dataframe that will be filled
    out = pd.DataFrame()
    
    # Loop to get the data for each book in the page
    for link in links:
        
        # Show which book we are getting the data
        print(link['href'])
        
        # get the link
        html = requests.get(main_url + link['href'], headers = headers) 
        
        # New soup
        bs = BeautifulSoup(html.content, 'html.parser') 
    
        # This dictionary will have all the columns (values) that we want
        a = {}
        
        # Get the title, price, stock, etc...
        a['title'] = bs.find('h1', class_ = 'font-product-title').text
        a['price'] = bs.find('span', class_ = 'lbl-price').text
        a['stock'] = bs.find('span', class_ = 'in-stock').text
        a['model'] = bs.find('span', class_ = 'name').next_sibling.next_sibling.text
        a['description'] = bs.find('div', itemprop = 'description').text
        
        # There's a table which has some values (but some items does not have the same columns)
        # We iterate in all the childrens and stores its values in the dictionary a
        table = bs.find('table', class_ = 'gvi-name-value')
        
        for child in table.find_all('tr'):
            
            if child != '\n': # avoid black line
                key_ = child.text.strip().split('\n')
                a[key_[0]] = key_[1]
        
        # We add the data for the link 
        out = pd.concat([out, pd.DataFrame.from_dict([a])])
        out = out.reset_index(drop = True)
        
        # We sleep for a while in order to seem like a real person.
        time.sleep(10) 
        
    return out
        
main = pd.DataFrame()

page_numbers = range(1, pages_to_scrape + 1)

# Loop to get the data for the pages we want.
for page_number in page_numbers:
    
    print(str(page_number))
    get_ = get_data_page(main_url + '?page=' + str(page_number))
    main = pd.concat([main, get_])
    
    time.sleep(7)
    print(page_number)
    
# Fixed some data type in the data
main['price'] = main['price'].str.split('$', expand = True)[1].str.replace(',','').astype('float64')

main['Número de Cuerdas'] = main['Número de Cuerdas'].fillna(0).astype('int64')
main['Número de Cuerdas'] = np.where(main['Número de Cuerdas'] == 0, np.nan, main['Número de Cuerdas'])

main['Numero de Trastes'] = main['Numero de Trastes'].fillna(0).astype('int64')
main['Numero de Trastes'] = np.where(main['Numero de Trastes'] == 0, np.nan, main['Numero de Trastes'])

# The scale length of a guitar is the distance between the guitar's nut and the bridge
main['scale'] = main['Escala'].str.split('(', expand = True)[1].str.split('mm', expand = True)[0].fillna(0).astype('int64')
main['scale'] = np.where(main['scale'] == 0, np.nan, main['scale'])

# The radius of the tuning fork is nothing more than the measure of that circumference
main['radius'] = main['Radio Diapason'].str.split('(', expand = True)[1].str.split('mm', expand = True)[0].fillna(0).astype('float64')
main['radius'] = np.where(main['radius'] == 0, np.nan, main['radius'])