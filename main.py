# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import csv
import re
import os

# Check if results directory exist
# if not : create it
if os.path.isdir("results") is False:
    os.mkdir("results")

# Define parent directory
parent_dir = os.path.join(os.getcwd(), "results")

# Base website url
website_url: str = "http://books.toscrape.com/"

# store all page links , for futur use.
# paging : list = [ "http://books.toscrape.com/" + "catalogue/page-{}.html".format(e) for e in range(1,50)]

# Create new request object
# use url (page_link later with a while loop) as arg
request_response = requests.get(website_url)
# check if website is reachable
if request_response.ok:

    # Create a new soup instance, take request_response.text
    # and a parser as argument.
    # if parser not set, bs4 will set one automatically
    # using .content and not text to get data has byte
    # to avoid utf8 problems
    soup = BeautifulSoup(request_response.content, "html.parser")
    # current = (soup.find('li', class_="current").text).split()[-1]

    # Get book collection url and category
    # stock it in dict
    # ignore "Books" because it's all books...
    books_category: dict = {
        (category.text)
        .replace(" ", "")
        .replace("\n", ""): "{}".format(website_url + category["href"])
        for category in soup.find("div", class_="side_categories")
        .find("ul", class_="nav nav-list")
        .findAll("a")
        if (category.text).replace(" ", "").replace("\n", "") != "Books"
    }
    for cat, url in books_category.items():
        # check if every category have directory
        # if not : create it
        if os.path.exists(os.path.join(parent_dir, cat)) is False:
            os.mkdir(os.path.join(parent_dir, cat))
        # get category pwd
        category_pwd : str = os.path.join(parent_dir, cat)
        # check if every category have img direct
        # if not : create it.
        if os.path.exists(os.path.join(category_pwd, "img")) is False:
            os.mkdir(os.path.join(category_pwd, "img"))
            # Define img_directory variable
        img_directory : str = os.path.join(category_pwd, "img")
        # Create new request object
        selected_book_category_url_request = requests.get(url)
        # check if website is reachable
        if selected_book_category_url_request.ok:
            # reset book_url_list
            book_url_list : list = []
            # Create a new soup instance, take selected_book_category_url.text
            # using .content and not text to get data has byte
            # to avoid utf8 problems
            soup = BeautifulSoup(
                selected_book_category_url_request.content, "html.parser"
            )
            # Get page number per books category
            book_category_number_of_page: int = int(
                (soup.find("li", class_="current").text).split()[-1]
                if soup.find("li", class_="current") is not None
                else 1
            )
            # loop all page on book category
            for i in range(1, book_category_number_of_page + 1):
                # delete index.html in url
                # add page number taken from for loop
                category_page_url: str = (
                    url.replace("index.html", "") + "page-{}.html".format(i)
                    if i > 1
                    else url
                )

                category_page_url_request = requests.get(category_page_url)
                # check if website is reachable
                if category_page_url_request.ok:
                    print("Working on : {}".format(cat))

                    # Create a new soup instance, take selected_book_category_url.text
                    # using .content and not text to get data has byte
                    # to avoid utf8 problems
                    soup = BeautifulSoup(
                        category_page_url_request.content, "html.parser"
                    )

                    # Find all books url on page
                    for book in soup.find_all("div", class_="image_container"):
                        book_url = website_url + "catalogue/" + (
                            book.find("a")["href"]
                        ).replace("../", "")
                        selected_book_url_request = requests.get(book_url)
                        if selected_book_url_request.ok:
                            soup = BeautifulSoup(
                                selected_book_url_request.content, "html.parser"
                            )

                            # Find all td inside a table which it have "table-striped" class
                            # there is no class to search these elements, that's why i use those loops
                            section_title: list = [
                                (element.text).lower().replace(" ", "_")
                                for element in soup.find(
                                    "table", class_="table-striped"
                                ).findAll("th")
                            ]
                            section_content: list = [
                                element.text
                                for element in soup.find(
                                    "table", class_="table-striped"
                                ).findAll("td")
                            ]
                            # Create new dict to store all data recieved
                            section_merged_dict: dict = {
                                section_title[i]: section_content[i]
                                for i in range(len(section_title))
                            }
                            # Get product title
                            title: str = (
                                soup.find("div", class_="product_main").find("h1").text
                            )
                            # Get product description
                            try:
                                product_description: str = (
                                    soup.find("div", {"id": "product_description"})
                                    .find_next("p")
                                    .text
                                )
                            except AttributeError:
                                pass
                            # category : str = (soup.find('li', class_= 'active').find_previous('li').text).replace('\n','')
                            # review_rating DON'T WORK.
                            review_rating_value = {
                                "One": 1,
                                "Two": 2,
                                "Three": 3,
                                "Four": 4,
                                "Five": 5,
                            }
                            review_rating: str = soup.find("p", class_="star-rating")[
                                "class"
                            ][1]
                            image_url: str = "{}{}".format(
                                website_url,
                                soup.find("img")["src"].replace("../", ""),
                            )

                            # Store all fields used in csv file.
                            fields: list = [
                                "product_page_url",
                                "universal_product_code(upc)",
                                "title",
                                "price_including_tax",
                                "price_excluding_tax",
                                "number_available",
                                "category",
                                "review_rating",
                                "image_url",
                                "product_description",
                            ]

                            # Store every data collected in list
                            infos: list = [
                                book_url,
                                section_merged_dict["upc"],
                                title,
                                section_merged_dict["price_(incl._tax)"],
                                section_merged_dict["price_(excl._tax)"],
                                section_merged_dict["availability"],
                                section_merged_dict["product_type"],
                                review_rating_value[review_rating]
                                if review_rating in review_rating_value
                                else "O",
                                image_url,
                                product_description,
                            ]

                            # Check if img exists in his directory
                            # if False : create it.
                            if (
                                os.path.isfile(
                                    os.path.join(
                                        img_directory, (image_url.split("/")[-1])
                                    )
                                )
                                is False
                            ):
                                img_name : str = image_url.split("/")[-1]
                                with urlopen(image_url) as img_data:
                                    # opened in write binary ; used when you are not writing common text
                                    # for image, video etc
                                    with open(
                                        os.path.join(
                                            img_directory, (image_url.split("/")[-1])
                                        ),
                                        "wb",
                                    ) as image:
                                        image.write(img_data.read())

                            this_book : str = os.path.join(category_pwd, cat + ".csv")
                            # check if "this_book".csv exists
                            # if it returns False then:
                            # create it in write mod and
                            # add headers + content
                            # else :
                            # open it in append mod and
                            # add content only
                            if os.path.isfile(this_book) is False:
                                # open result.csv in write mode
                                with open(
                                    this_book, "w", encoding="utf8", newline=""
                                ) as file:
                                    file_writer = csv.writer(
                                        file, delimiter=";", dialect="excel"
                                    )
                                    file_writer.writerow(fields)
                                    file_writer.writerow(infos)
                            else:
                                # open result.csv in write mode
                                with open(
                                    this_book, "a", encoding="utf8", newline=""
                                ) as file:
                                    file_writer = csv.writer(
                                        file, delimiter=";", dialect="excel"
                                    )
                                    file_writer.writerow(infos)
