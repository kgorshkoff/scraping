import json

import scrapy
from scrapy.http.response import Response

from gbdm.items import InstagramPostItem, InstagramAuthorItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']

    __urls = {
        'login': 'https://www.instagram.com/accounts/login/ajax/',
        'tag': '/explore/tags/наука/'
    }

    __api_query = {
        'url': '/graphql/query/',
        'posts': 'c769cb6c71b24c8a86590b22402fda50',
        'user': 'd4d88dc1500312af6f937f7b804c68c3'
    }

    def __init__(self, *args, **kwargs):
        self.__login = kwargs['login']
        self.__password = kwargs['password']
        super().__init__(*args, **kwargs)

    def parse(self, response: Response, **kwargs):
        try:
            js_data = self.get_js_shared_data(response)

            yield scrapy.FormRequest(self.__urls['login'],
                                     method='POST',
                                     callback=self.parse,
                                     formdata={'username': self.__login,
                                               'enc_password': self.__password},
                                     headers={'X-CSRFToken': js_data['config']['csrf_token']},
                                     )
        except AttributeError as e:
            if response.json().get('authenticated'):
                yield response.follow(self.__urls['tag'], callback=self.tag_page_parse)

    def tag_page_parse(self, response: Response, first_run=True):
        if first_run:
            js_data = self.get_js_shared_data(response)
            json_data = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']
        else:
            json_data = response.json()['data']['hashtag']

        variables = {"tag_name": json_data['name'],
                     "first": 50,
                     "after": json_data['edge_hashtag_to_media']['page_info']['end_cursor']}

        url = f'{self.__api_query["url"]}?query_hash={self.__api_query["posts"]}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_api_hashtag_posts)
        if json_data['edge_hashtag_to_media']['page_info']['has_next_page']:
            yield response.follow(url, callback=self.tag_page_parse, cb_kwargs={'first_run': False}, dont_filter=True)

    def get_api_hashtag_posts(self, response: Response):
        posts = response.json()['data']['hashtag']['edge_hashtag_to_media']['edges']
        for post in posts:
            item = InstagramPostItem()
            for key, value in post['node'].items():
                if key.startswith('__'):
                    item[key[2:]] = value
                    continue
                item[key] = value
            yield item

            if post['node']['edge_liked_by']['count'] > 100 or post['node']['edge_media_to_comment']['count'] > 30:
                variables = {"user_id": post['node']['owner']['id'],
                             "include_chaining": True,
                             "include_reel": True,
                             "include_suggested_users": False,
                             "include_logged_out_extras": False,
                             "include_highlight_reels": True,
                             "include_live_status": True}

                url = f'https://www.instagram.com{self.__api_query["url"]}?query_hash' \
                      f'={self.__api_query["user"]}&variables={json.dumps(variables)}'
                yield response.follow(url, callback=self.get_api_user)

    def get_api_user(self, response: Response):
        item = InstagramAuthorItem()
        user = response.json()
        for key, value in user['data']['user']['reel'].items():
            if key.startswith('__'):
                item[key[2:]] = value
                continue
            item[key] = value
        yield item

    @staticmethod
    def get_js_shared_data(response):
        marker = "window._sharedData = "
        data = response.xpath(
            f'/html/body/script[@type="text/javascript" and contains(text(), "{marker}")]/text()') \
            .extract_first()
        data = data.replace(marker, '')[:-1]
        return json.loads(data)
