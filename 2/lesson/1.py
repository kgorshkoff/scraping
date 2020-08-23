from typing import List, Dict

import re
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


class GBBlogParser:
    domain = 'https://geekbrains.ru'
    start_url = 'https://geekbrains.ru/posts'

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client['parse_gb_blog']
        self.collection = self.db['posts']
        self.visited_urls = set()
        self.post_links = set()
        self.post_data = []

    def parse_rows(self, url=start_url):
        while url:
            if url in self.visited_urls:
                break
            response = requests.get(url)
            self.visited_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
            url = self.get_next_page(soup)
            self.search_post_links(soup)

    def get_next_page(self, soup: BeautifulSoup) -> str:
        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        a = ul.find('a', text="›")
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    def search_post_links(self, soup: BeautifulSoup) -> List[str]:
        wrapper = soup.find('div', attrs={'class': 'post-items-wrapper'})
        posts = wrapper.find_all('div', attrs={'class': 'post-item'})
        links = {f'{self.domain}{itm.find("a").get("href")}' for itm in posts}
        self.post_links.update(links)

    def post_page_parse(self):
        for url in self.post_links:
            if url in self.visited_urls:
                continue
            response = requests.get(url)
            self.visited_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
            if len(self.post_data) > 5:
                break
            self.post_data.append(self.get_post_data(soup))

    def get_post_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        result = {}
        result['title'] = soup.find('h1', attrs={'class':'blogpost-title'}).text
        content = soup.find('div', attrs={'class': 'blogpost-content', 'itemprop': 'articleBody'})
        img = content.find('img')
        result['image'] = img.get('src') if img else None
        return result

    def save_to_mongo(self):
        self.collection.insert_many(self.post_data)
        print('Данные сохранены')


if __name__ == '__main__':
    parser = GBBlogParser()
    parser.parse_rows()
    parser.post_page_parse()
    parser.save_to_mongo()
    print(1)
