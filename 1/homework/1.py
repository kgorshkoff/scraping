import json
import time

import requests
from tqdm import tqdm


class Parser5ka:
    _domain = 'https://5ka.ru'
    _offers_path = '/api/v2/special_offers/'
    _categories_path = '/api/v2/categories/'

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                      "Version/13.1.2 Safari/605.1.15"
    }

    def __init__(self):
        self.products = []

    def get_structure(self):
        try:
            categories = requests.get(self._domain + self._categories_path, headers=self.headers)
            self.structure = categories.json()
        except ValueError as e:
            return 'There was an error getting categories from url: ' + e

    def download(self):
        self.get_structure()
        for category in tqdm(self.structure):
            url = self._domain + self._offers_path
            params = {
                'records_per_page': 20,
                'categories': int(category['parent_group_code'])
            }
            while url:
                response = requests.get(url, headers=self.headers, params=params)
                try:
                    data = response.json()
                except ValueError:
                    print('Not a JSON in response, probably an error somewhere in the link')

                params = {}
                url = data['next']
                if data['results']:
                    if category.get('products'):
                        category['products'].extend(data['results'])
                    else:
                        category['products'] = data['results']
                time.sleep(0.1)

    def save_data(self):
        for item in self.structure:
            if item.get('products'):
                with open(item['parent_group_code'] + '.json', 'w', encoding='UTF-8') as f:
                    f.write(json.dumps(item, ensure_ascii=False))


if __name__ == '__main__':
    parser = Parser5ka()

    parser.download()
    parser.save_data()
