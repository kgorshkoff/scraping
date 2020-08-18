import asyncio
from aiohttp import ClientSession
import lxml
from time import sleep
from datetime import datetime


from typing import List, Dict
from bs4 import BeautifulSoup
from pymongo import MongoClient


class GBBlogParser:
    domain = 'https://geekbrains.ru'
    default_url = 'https://geekbrains.ru/posts?page=1'

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client['parse_gb_blog']
        self.collection = self.db['posts']
        self.visited_urls = set()
        self.post_links = set()
        self.post_data = []
        self.tasks = []
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, "
                                      "like Gecko) Version/13.1.2 Safari/605.1.15"}

        # self.links_to_visit = {self.default_url, }

    async def fetch_url(self, url, session):
        if url in self.visited_urls:
            return
        async with session.get(url, headers=self.headers) as response:
            self.visited_urls.add(url)
            resp = await response.read()
            soup = BeautifulSoup(resp, 'lxml')
            if self.default_url[:-1] in url:
                await self.run(self.search_post_links(soup))
                await self.run(self.get_next_page(soup))
            else:
                self.post_data.append(self.get_post_data(soup))

    async def bound_fetch(self, sem, url, session):
        async with sem:
            await self.fetch_url(url, session)

    async def run(self, urls=[default_url]):
        sem = asyncio.Semaphore(100)

        async with ClientSession() as session:
            for url in urls:
                task = asyncio.create_task(self.fetch_url(url, session))
                self.tasks.append(task)
                sleep(0.1)

            responses = asyncio.gather(*self.tasks)
            await responses

    def get_next_page(self, soup: BeautifulSoup) -> str:
        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        a = ul.find('a', text="›")
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    def get_post_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        result = {}
        result['url'] = soup.find('link', attrs={'rel': 'canonical'}).get('href')
        result['title'] = soup.find('h1', attrs={'class':'blogpost-title'}).text
        content = soup.find('div', attrs={'class': 'blogpost-content', 'itemprop': 'articleBody'})
        img = content.find('img')
        result['image'] = img.get('src') if img else None
        author_data = soup.find('div', attrs={'class': 'text-lg', 'itemprop': 'author'}).parent
        result['author'] = author_data.find('div', attrs={'class': 'text-lg', 'itemprop': 'author'}).text
        result['author_url'] = self.domain + author_data.get('href')
        dt = soup.find('time', attrs={'class': 'text-md', 'itemprop': 'datePublished'}).get('datetime')
        result['date_published'] = datetime.fromisoformat(dt)
        return result

    def search_post_links(self, soup: BeautifulSoup) -> List[str]:
        wrapper = soup.find('div', attrs={'class': 'post-items-wrapper'})
        posts = wrapper.find_all('div', attrs={'class': 'post-item'})
        links = {f'{self.domain}{itm.find("a").get("href")}' for itm in posts}
        return list(links)

    def save_to_mongo(self):
        self.collection.insert_many(self.post_data)
        print('Данные сохранены')

    def get_posts_from_db(self, startdate: str, enddate: str):
        # start and enddate expected in iso format
        startdate = datetime.fromisoformat(startdate)
        enddate = datetime.fromisoformat(enddate)

        cursor = self.collection.find({'date_published': {'$gte': startdate, '$lt': enddate}})
        for doc in cursor:
            print(doc)


if __name__ == '__main__':
    parser = GBBlogParser()
    asyncio.run(parser.run())

    print(1)
