import json
import re
import asyncio
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://quotes.toscrape.com'

author_list = []
unique_author = set()   # допоміжний сет для збирання тільки "унікальних" авторів
quote_list = []
page_list = []  # для формування списку url, на яких будемо парсити


def get_info_about_author(about_link):
    path = BASE_URL + about_link
    response1 = requests.get(path)
    soup1 = BeautifulSoup(response1.text, 'lxml')
    born_date = soup1.find('span', class_='author-born-date').text
    born_location = soup1.find('span', class_='author-born-location').text
    description = soup1.find('div', class_='author-description').text
    return born_date, born_location, description.strip()


def one_page_parse(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('span', class_='text')
    authors = soup.find_all('small', class_='author')
    author_details = soup.select('div[class=quote] span a')
    tags = soup.find_all('div', class_='tags')

    for i in range(0, len(quotes)):
        aut = dict()
        author = authors[i].text.strip().title()
        aut['fullname'] = author

        # формуємо список тільки з "унікальних" авторів:
        if author not in unique_author:
            about_link = author_details[i]['href']
            aut['born_date'], aut['born_location'], aut['description'] = get_info_about_author(about_link)
            author_list.append(aut)
            unique_author.add(author)

        quote = dict()
        tgs = []
        tags_for_quote = tags[i].find_all('a', class_='tag')
        for tag_for_quote in tags_for_quote:
            tgs.append(tag_for_quote.text)
        quote['author'] = author
        quote['quote'] = quotes[i].text
        quote['tags'] = tgs
        quote_list.append(quote)


async def main():
    i = 1
    while True:
        # формуємо список сторінок на яких будемо парсити:
        number_page_link = f'https://quotes.toscrape.com/page/{i}'
        response = requests.get(number_page_link)

        if not re.findall('No quotes found!', response.text):
            page_list.append(number_page_link)
            i += 1
        else:
            break
    # асинхронно парсимо по всьому списку сторінок:
    tasks = [asyncio.create_task(one_page_parse(url) for url in page_list)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

    with open('authors.json', 'w', encoding='utf-8') as fd:
        json.dump(author_list, fd, ensure_ascii=False)

    with open('quotes.json', 'w', encoding='utf-8') as f:
        json.dump(quote_list, f, ensure_ascii=False)
