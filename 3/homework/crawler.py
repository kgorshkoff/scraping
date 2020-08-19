from typing import List, Dict, Set

import re
import json
import lxml
import requests
from bs4 import BeautifulSoup


class GBBlogParser:
    domain = 'https://habr.com'
    start_url = 'https://habr.com/ru/top/'

    def __init__(self):
        self.visited_urls = set()
        self.post_links = set()
        self.post_data = []
        self.headers = {
            'User-Agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:79.0) Gecko/20100101 '
                          'Firefox/79.0 '
        }

    def parse_rows(self, url=start_url):
        while url:
            if url in self.visited_urls:
                break
            response = requests.get(url, headers=self.headers)
            self.visited_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
            url = self.get_next_page(soup)
            self.post_links.update(self.search_post_links(soup))

    def get_next_page(self, soup: BeautifulSoup) -> str:
        ul = soup.find('ul', attrs={'class': 'arrows-pagination'})
        a = ul.find('a', attrs={'id': 'next_page'})
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    def search_post_links(self, soup: BeautifulSoup) -> Set[str]:
        wrapper = soup.find('div', attrs={'class': 'posts_list'})
        posts = wrapper.find_all('a', attrs={'class': 'post__title_link'})
        links = {f'{itm.get("href")}' for itm in posts}
        return links

    def post_page_parse(self):
        for url in self.post_links:
            if url in self.visited_urls:
                continue
            response = requests.get(url)
            self.visited_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
            self.post_data.append(self.get_post_data(soup))

    def get_post_data(self, soup: BeautifulSoup) -> Dict[str, List]:
        result = {}
        result['url'] = soup.find('meta', attrs={'property': 'og:url'}).get('content')
        result['title'] = soup.find('meta', attrs={'property': 'og:title'}).get('content')

        post_additionals = soup.find('div', attrs={'class': 'post-additionals'})
        user_data = post_additionals.find('div', attrs={'class': 'user-info'})
        result['author'] = []

        result['author'].append({
            'name': user_data.find('a', attrs={'class': re.compile('user-info__[a-z]{8}')}).text,
            'url': f'https://habr.com/users/{user_data.get("data-user-login")}/'
        })

        post_wrapper = soup.find('div', attrs={'class': 'post__wrapper'})

        tags = post_wrapper.find('ul', attrs={'class': 'js-post-tags'}).find_all('a')
        result['tags'] = []
        for tag in tags:
            result['tags'].append({'name': tag.get_text(strip=True), 'url': tag.get('href')})

        hubs = post_wrapper.find('ul', attrs={'class': 'js-post-hubs'}).find_all('a')
        result['hubs'] = []
        for hub in hubs:
            result['hubs'].append({'name': hub.get_text(strip=True), 'url': hub.get('href')})
        return result

    def save_to_file(self):
        with open('temp.json', 'w') as f:
            json.dump(self.post_data, f)

    def load_from_file(self):
        with open('temp.json', 'r') as f:
            self.post_data = json.load(f)
