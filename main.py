# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import csv
import re

url : str = 'http://books.toscrape.com/' 

# store all page links , for futur use.
# paging : list = [ "http://books.toscrape.com/" + "catalogue/page-{}.html".format(e) for e in range(1,50)]

# Create new request object
# use url (page_link later with a while loop) as arg
request_response = requests.get(url)
# check if website is reachable
if request_response.ok:
    # Create a new soup instance, take request_response.text
    # and a parser as argument.
    # if parser not set, bs4 will set one automatically
    # using .content and not text to get data has byte
    # to avoid utf8 problems
    soup = BeautifulSoup(request_response.content, 'html.parser')
    
    # Get book url and concat it with url var
    book_url : str = "{}{}".format(url, soup.find('a', {'title': 'Sharp Objects'})['href'])
    
    # Create new request object
    selected_book_request_response = requests.get(book_url)
    # check if website is reachable
    if selected_book_request_response.ok:
    
        # Create a new soup instance, take selected_book_request_response.text
        # using .content and not text to get data has byte
        # to avoid utf8 problems
        soup = BeautifulSoup(selected_book_request_response.content, 'html.parser')
        
        # Find all td inside a table which it have "table-striped" class
        # there is no class to search these elements, that's why i use those loops
        section_title : list = [(element.text).lower().replace(' ', '_') for element in soup.find('table', class_= 'table-striped').findAll('th')]
        section_content : list = [element.text for element in soup.find('table', class_= 'table-striped').findAll('td')]
        print(section_title, section_content)
        # Create new dict to store all data recieved
        section_merged_dict : dict = {section_title[i]: section_content[i] for i in range(len(section_title))}
        
        title : str = soup.find('div', class_='product_main').find('h1').text
        # regexp: check if there is whitespace and replace them by whitespace (used to remove multiple whitespace)
        number_available : str = re.sub('\s+',' ', (soup.find('p', class_= 'instock availability').text).replace('\n', ''))
        product_description : str = soup.find('div', {'id': 'product_description'}).find_next('p').text
        category : str = (soup.find('li', class_= 'active').find_previous('li').text).replace('\n','')
        # review_rating DON'T WORK.
        review_rating : str = len(soup.find("p", class_ = 'star-rating').findAll('i', attrs={'style': 'color:#E6CE31'})) 
        image_url : str = "{}{}".format(url, soup.find("img")['src'].replace('../', ''))
        
        # Store all fields used in csv file.
        fields : list = [
        'product_page_url',
        'universal_product_code(upc)',
        'title',
        'price_including_tax',
        'price_excluding_tax',
        'number_available',
        'category',
        'review_rating',
        'image_url',
        'product_description',
        ]
        
        # Store every data collected in list
        infos : list = [
        book_url, 
        section_merged_dict['upc'],
        title,
        section_merged_dict['price_(incl._tax)'],
        section_merged_dict['price_(excl._tax)'],
        number_available,
        category,
        review_rating if review_rating else 'O',
        image_url,
        product_description,
        ]
        
        print(infos)
        # open result.csv in write mode 
        with open('result.csv', 'w', encoding='utf8') as file:
            file_writer = csv.writer(file, dialect="excel-tab")
            file_writer.writerow([fields])
            file_writer.writerow([infos])
            
            
            
        