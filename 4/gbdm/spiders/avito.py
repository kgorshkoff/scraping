import scrapy
import pytesseract
from PIL import Image
import io
import base64


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    start_urls = ['https://www.avito.ru/himki/kvartiry/prodam']

    __xpath_query = {
        'pagination': '//div[@class="index-content-2lnSO"]//'
                      'div[contains(@data-marker, "pagination-button")]/'
                      'span[@class="pagination-item-1WyVp"]/@data-marker',
        'ads': "//h3[@class='snippet-title']/a[@class='snippet-link'][@itemprop='url']/@href",
        'ad_title': '//div[@class="title-info-main"]/h1[@class="title-info-title"]/'
                    'span[@class="title-info-title-text"]/text()',
        'ad_params': '//ul[@class="item-params-list"]/li[@class="item-params-list-item"]',
        'ad_gallery': '//div[@class="gallery-imgs-container js-gallery-imgs-container"]'
                      '/div[@class="gallery-img-wrapper js-gallery-img-wrapper"]/div[1]/@data-url',
        'ad_prices': '//div[@class="price-value-prices-wrapper"]'
                     '/ul[@class="price-value-prices-list js-price-value-prices-list"]/li',
        'ad_address': '//div[@class="item-address"]/div[@itemprop="address"]/span/text()'
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
        ad = {}
        ad['url'] = response.url
        ad['title'] = response.xpath(self.__xpath_query['ad_title']).get()
        ad['address'] = response.xpath(self.__xpath_query['ad_address']).get().strip()

        gallery = response.xpath(self.__xpath_query['ad_gallery']).getall()
        ad['photo'] = ['https:' + url if url[:2] == '//' else url for url in gallery]

        price_wrapper = response.xpath(self.__xpath_query['ad_prices'])
        prices = price_wrapper.xpath('text()').getall()
        prices = [price.encode('ascii', 'ignore').decode().strip() for price in prices if price != '\n ']
        currencies = price_wrapper.xpath('span/text()|span/span/text()').extract()

        ad['price'] = []
        for i in range(len(set(currencies))):
            ad['price'].append({'currency ' + currencies[i]: (prices[i], prices[i + len(set(currencies))])})

        param_wrapper = response.xpath(self.__xpath_query['ad_params'])
        keys = param_wrapper.xpath('span[@class="item-params-label"]/text()').extract()
        values = param_wrapper.xpath('text()|a/text()').extract()
        values = [v.strip() for v in values if v.strip() != '']
        ad['params'] = []
        for i in range(len(keys)):
            ad['params'].append({keys[i][:-2]: values[i]})

        request = scrapy.Request(f'https://www.avito.ru/items/phone/{response.url.split("_")[-1]}?=&vsrc=r',
                                 callback=self.ads_phone_parse)

        request.cb_kwargs['ad'] = ad
        yield request

    def ads_phone_parse(self, response, ad):
        b64_image_string = response.text.split('base64,')[-1][:-2]
        b64_obj = io.BytesIO(base64.b64decode(b64_image_string))
        image = Image.open(b64_obj)
        ad['phone'] = pytesseract.image_to_string(image).strip()

        yield ad
