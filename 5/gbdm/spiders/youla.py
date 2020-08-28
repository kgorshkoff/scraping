import scrapy
from scrapy.loader import ItemLoader

import re
import urllib
from gbdm.items import YoulaItem


class YoulaSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/moskva/cars/used/chery']

    __xpath_query = {
        'pagination': '//div[contains(@class,"Paginator_block__2XAPy")]/div[@class="Paginator_total__oFW1n"]/text()',

        'ads': '//div[@id="serp"]/span/article//a[@data-target="serp-snippet-title"]/@href'
    }

    __xpath_ad_query = {
        'title':    '//div[contains(@class, "AdvertCard_pageContent__24SCy")]'
                    '/div[@class="AdvertCard_topAdvertHeader__iqqNl"]'
                    '//div[@class="AdvertCard_advertTitle__1S1Ak"]/text()',

        'specs':    '//div[contains(@class, "AdvertCard_info__3IKjT")]/div[@class="AdvertCard_specs__2FEHc"]/div',

        'images':   '//div[@class="PhotoGallery_block__1ejQ1"]'
                    '/div[@class="PhotoGallery_photoWrapper__3m7yM"]'
                    '/figure/picture/img/@src',

        'price':    '//div[@class="AdvertCard_topAdvertHeader__iqqNl"]'
                    '/div[@class="AdvertCard_priceBlock__1hOQW"]'
                    '/div[@data-target="advert-price"]'
                    '/text()',

        'description': '//div[contains(@class, "AdvertCard_description__2bVlR")]//div//div/text()',

        'phone': '//div[@class="advert__sticky-bottom-wrapper"]/div/div/a/@href'
    }

    def parse(self, response, first_run=True):
        if first_run:
            pages_count = int(response.xpath(self.__xpath_query['pagination']).extract()[1])

            for num in range(2, pages_count + 1):
                yield response.follow(
                    f'page={num}',
                    callback=self.parse,
                    cb_kwargs={'first_run': False}
                )

        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse
            )

    def ads_parse(self, response):
        item_loader = ItemLoader(YoulaItem(), response)

        for key, value in self.__xpath_ad_query.items():
            item_loader.add_xpath(key, value)
        item_loader.add_value('url', response.url)
        if '/prv--' in response.url:
            sellerLink = urllib.parse.unquote(response.text).split('youlaId","')[2].split('"')[0]
        else:
            sellerLink = urllib.parse.unquote(response.text).split('sellerLink","')[1].split('"')[0]

        item_loader.add_value('seller', 'https://auto.youla.ru' + sellerLink)

        yield scrapy.Request(url=response.url,
                             callback=self.phone_parse,
                             headers={'User-Agent': 'Mozilla/5.0 (Android 10; Mobile; rv:79.0) Gecko/79.0 Firefox/79.0'},
                             cb_kwargs={'item_loader': item_loader},
                             dont_filter=True)

    def phone_parse(self, response, item_loader):
        item_loader.add_value('phone', response.xpath(self.__xpath_ad_query['phone']).extract())
        yield item_loader.load_item()
