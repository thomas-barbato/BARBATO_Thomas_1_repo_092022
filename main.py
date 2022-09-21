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
    soup = BeautifulSoup(request_response.text, 'html.parser')
    # Get book url and concat it with url var
    book_url : str = "{}{}".format(url, soup.find('a', {'title': 'Sharp Objects'})['href'])
    # Create new request object
    selected_book_request_response = requests.get(book_url)
    # Create a new soup instance, take selected_book_request_response.text
    soup = BeautifulSoup(selected_book_request_response.text, 'html.parser')
    # Find all td inside a table which it have "table-striped" class
    # there is no class to search these elements, that's why i use those loops
    section_title : list = [(element.text).lower().replace(' ', '_') for element in soup.find('table', {'class': 'table-striped'}).findAll('th')]
    section_content : list = [element.text for element in soup.find('table', {'class': 'table-striped'}).findAll('td')]
    # Create new dict to store all data recieved
    section_merged_dict : dict = {section_title[i]: section_content[i] for i in range(len(section_title))}
    title : str = soup.find('div', {'class','product_main'}).find('h1').text
    # regexp: check if there is whitespace and replace it by whitespace (used to remove multiple whitespace)
    number_available : str = re.sub('\s+',' ', (soup.find('p', {'class': 'instock availability'}).text).replace('\n', ''))
    product_description : str = soup.find('div', {'id': 'product_description'}).find_next('p').text
    category : str = soup.find('li', {'class': 'active'}).find_previous('li').text
    review_rating : str = soup.find("p", {'class': 'star-rating'}).findAll('i', attrs={'style': 'color:#E6CE31'})
    image_url : str = "{}{}".format(url, soup.find("img")['src'].replace('../', ''))
    
    fields : list = [
        'product_page_url',
        'universal_ product_code (upc)',
        'title',
        'price_including_tax',
        'price_excluding_tax',
        'number_available',
        'product_description',
        'category',
        'review_rating',
        'image_url'
    ]
    data : dict = {
        'product_page_url' : book_url,
        'universal_ product_code (upc)': section_merged_dict['upc'],
        'title' : title,
        'price_including_tax': section_merged_dict['price_(incl._tax)'],
        'price_excluding_tax': section_merged_dict['price_(excl._tax)'],
        'number_available': number_available,
        'product_description': product_description,
        'category': category,
        'review_rating' : review_rating,
        'image_url' : image_url
    }
    
    
    # open result.csv in write mode 
    with open('result.csv', 'w', encoding='UTF8', newline='') as file:
        fieldnames = ['title', 'content']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for field in fields:
            writer.writerow({'title': field, 'content': data[field]})
        
        