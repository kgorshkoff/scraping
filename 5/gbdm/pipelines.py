# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline


class GbdmPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=f'mongodb://{crawler.settings.get("MONGODB_SERVER")}:{crawler.settings.get("MONGODB_PORT")}',
            mongo_db=crawler.spider.name
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection = self.db[type(item).__name__]
        collection.update({'url': item['url']}, item, upsert=True)
        return item


class GbdmImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item.get('images', []):
            try:
                yield Request(url)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results if itm[0]]
        return item
