import os
from pathlib import Path

from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gbdm import settings
from gbdm.spiders.instagram import InstagramSpider

if __name__ == '__main__':
    load_dotenv(dotenv_path=Path('.env').absolute())
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)

    crawl_proc = CrawlerProcess(settings=crawl_settings)

    # crawl_proc.crawl(AvitoSpider)
    # crawl_proc.crawl(YoulaSpider)

    crawl_proc.crawl(InstagramSpider, login=os.getenv('USERNAME'), password=os.getenv('ENC_PASSWORD'))
    crawl_proc.start()
