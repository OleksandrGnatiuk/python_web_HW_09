import json

import requests
from bs4 import BeautifulSoup

url = 'https://quotes.toscrape.com'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
quotes = soup.find_all('span', class_='text')
authors = soup.find_all('small', class_='author')
author_details = soup.select('div[class=quote] span a')
tags = soup.find_all('div', class_='tags')


def get_about_author(about_link):
    path = url + about_link
    response1 = requests.get(path)
    soup1 = BeautifulSoup(response1.text, 'lxml')
    born_date = soup1.find('span', class_='author-born-date').text
    born_location = soup1.find('span', class_='author-born-location').text
    description = soup1.find('div', class_='author-description').text
    return born_date, born_location, description.strip()


author_list = []
quote_list = []

for i in range(0, len(quotes)):
    aut = dict()
    aut['fullname'] = authors[i].text
    about = author_details[i]['href']
    aut['born_date'], aut['born_location'], aut['description'] = get_about_author(about)
    author_list.append(aut)

    quote = dict()
    tgs = []

    tags_for_quote = tags[i].find_all('a', class_='tag')
    for tag_for_quote in tags_for_quote:
        tgs.append(tag_for_quote.text)

    quote['author'] = authors[i].text
    quote['quote'] = quotes[i].text
    quote['tags'] = tgs
    quote_list.append(quote)


with open('authors.json', 'w', encoding='utf-8') as fd:
    json.dump(author_list, fd, ensure_ascii=False)

with open('qoutes.json', 'w', encoding='utf-8') as f:
    json.dump(quote_list, f, ensure_ascii=False)