import scrapy
from scrapy.loader import ItemLoader

from gbdm.items import AvitoItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    start_urls = ['https://www.avito.ru/himki/kvartiry/prodam']

    __xpath_query = {
        'pagination': '//div[@class="index-content-2lnSO"]'
                      '//div[contains(@data-marker, "pagination-button")]'
                      '/span[@class="pagination-item-1WyVp"]/@data-marker',

        'ads': "//h3[@class='snippet-title']"
               "/a[@class='snippet-link'][@itemprop='url']"
               '/@href',

        'title': '//h1[@class="title-info-title"]'
                 '/span[@itemprop="name"]'
                 '/text()',

        'params': '//div[@class="item-params"]'
                  '/ul[@class="item-params-list"]'
                  '/li[@class="item-params-list-item"]',

        'images': '//div[@class="gallery-imgs-container js-gallery-imgs-container"]'
                  '/div[@class="gallery-img-wrapper js-gallery-img-wrapper"]'
                  '/div[1]'
                  '/@data-url',

        'prices': '//div[contains(@class, "price-value-prices-wrapper")]'
                  '/ul[contains(@class, "price-value-prices-list")]'
                  '/li[contains(@class, "price-value-prices-list-item_size-normal")]',

        'address': '//div[@class="item-address"]'
                   '/div[@itemprop="address"]'
                   '/span'
                   '/text()'
    }

    def parse(self, response, first_run=True):
        if first_run:
            pages_count = int(
                response.xpath(self.__xpath_query['pagination']).extract()[-1].split('(')[-1].replace(')', ''))

            for num in range(2, pages_count + 1):
                yield response.follow(
                    f'?p={num}',
                    callback=self.parse,
                    cb_kwargs={'first_run': False}
                )

        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse
            )

    def ads_parse(self, response):
        item_loader = ItemLoader(AvitoItem(), response)

        for key, value in self.__xpath_query.items():
            if key in ('ads', 'pagination'):
                continue
            item_loader.add_xpath(key, value)
        item_loader.add_value('url', response.url)

        yield scrapy.Request(url=f'https://www.avito.ru/items/phone/{response.url.split("_")[-1]}?=&vsrc=r',
                             callback=self.ads_get_phone,
                             cb_kwargs={'item_loader': item_loader})

    def ads_get_phone(self, response, item_loader):
        item_loader.add_value('phone', response.text.split('base64,')[-1][:-2])
        yield item_loader.load_item()
