import os
from pathlib import Path

import pymongo
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

mongo_server = '10.1.1.100'
mongo_port = '27017'


class MvideoScraper:
    def __init__(self, *args, **kwargs):
        self.driver = webdriver.Firefox()
        self.driver.get('https://www.mvideo.ru/promo/bolshaya-shkolnaya-rasprodazha-skidki-bolee-40-mark168010620')

        self.mongo_uri = f'mongodb://{kwargs["mongo_login"]}:{kwargs["mongo_password"]}@{mongo_server}:{mongo_port}'
        self.mongo_db = 'mvideo'
        self.mongo_collection = type(self).__name__
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    __xpath = {
        'pagination_next': '//div[@class="o-pagination-section"]/div[@class="c-pagination notranslate"]'
                           '/a[@class="c-pagination__next font-icon icon-up "]',
        'items': '//div[@data-init="productTileList"]//div[contains(@class, "product-tiles-list-wrapper")]/div',

        'details_button': '//ul[@class="c-tabs__menu-list"]/li',
        'details_categories': '//div[@class="product-details-specification-content"]/div[2]/div/h3',
        'details': '//div[@class="product-details-specification-content"]/div[2]/div'
                   '//table[@class="table table-striped product-details-table"]'
                   '//span[@class="product-details-overview-specification"]',
        'title': '//div[@class="o-pdp-topic__title"]/h1',
        'price': '//div[@class="c-pdp-price__summary"]/div[@class="c-pdp-price__offers"]'
                 '/div[contains(@class, "c-pdp-price__current")]'

    }

    def start(self):
        while True:
            items_len = len(self.wait_get_element(self.__xpath['items'], multiple=True))

            for index in range(0, items_len):
                items = self.wait_get_element(self.__xpath['items'], multiple=True)
                item = items[index]
                item.click()

                self.wait_get_element(self.__xpath['details_button'], multiple=True)[1].click()

                result = {
                    'title': self.driver.find_element_by_xpath(self.__xpath['title']).text,
                    'price': self.driver.find_element_by_xpath(self.__xpath['price']).text,
                    'params': {},
                }

                # details_categories = self.wait_get_element(self.__xpath['details_categories'], multiple=True)
                details = self.wait_get_element(self.__xpath['details'], multiple=True)

                for i in range(0, len(details), 2):
                    result['params'].update({details[i].text.replace('.', ''): details[i + 1].text})

                self.write_to_mongo(result)
                self.driver.execute_script('window.history.go(-2)')

            try:
                next_page = self.wait_get_element(self.__xpath_mail['pagination_next'])
                next_page.click()
            except Exception as e:
                print('No more pages to scrap')
                self.driver.quit()
                break

    def write_to_mongo(self, item):
        self.db[self.mongo_collection].insert_one(item)

    def wait_get_element(self, xpath, multiple=False, timeout=10):
        try:
            element_present = EC.presence_of_element_located((By.XPATH, xpath))
            WebDriverWait(self.driver, timeout).until(element_present)
            if multiple:
                return self.driver.find_elements_by_xpath(xpath)
            return self.driver.find_element_by_xpath(xpath)
        except TimeoutException:
            print("Timed out, shutting down")
            self.driver.quit()


if __name__ == '__main__':
    load_dotenv(dotenv_path=Path('.env').absolute())
    mail_crawler = MvideoScraper(
        mongo_login=os.getenv('MONGOLOGIN'),
        mongo_password=os.getenv('MONGOPASSWORD')
    )
    mail_crawler.start()
