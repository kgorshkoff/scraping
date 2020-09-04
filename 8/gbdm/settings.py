# Scrapy settings for gbdm project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os


def get_env_value(env_variable):
    try:
        return os.environ[env_variable]
    except KeyError:
        error_msg = 'env variable not set'
        raise AttributeError(error_msg)


BOT_NAME = 'gbdm'

SPIDER_MODULES = ['gbdm.spiders']
NEWSPIDER_MODULE = 'gbdm.spiders'

LOG_ENABLED = True
LOG_LEVEL = 'DEBUG'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:79.0) Gecko/20100101 Firefox/79.0'
# USER_AGENT = 'Mozilla/5.0 (Android 10; Mobile; rv:79.0) Gecko/79.0 Firefox/79.0'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 4

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 5
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    # 'gbdm.middlewares.GbdmSpiderMiddleware': 543,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'gbdm.middlewares.Retry429Middleware': 100,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
    # 'scrapy_rotated_proxy.downloadmiddlewares.proxy.RotatedProxyMiddleware': 750,
    #    'gbdm.middlewares.GbdmDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
IMAGES_STORE = 'images'

ITEM_PIPELINES = {
    'gbdm.pipelines.GbdmImagePipeline': 200,
    'gbdm.pipelines.GbdmPipeline': 300,
}

MONGODB_SERVER = '10.1.1.100'
MONGODB_PORT = 27017
# MONGO_USERNAME = get_env_value('MONGOUSERNAME')
# MONGO_PASSWORD = get_env_value('MONGOPASSWORD')

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


ROTATED_PROXY_ENABLED = False
ROTATING_PROXY_LIST = [
    '195.135.54.255: 8080',
    '217.64.109.231: 45282',
    '111.118.135.132: 56627',
    '176.110.121.90: 21776',
    '96.9.69.164:53281',
    '185.134.23.197:80',
    '138.68.60.8:8080',
    '193.200.151.69:48241',
    '110.74.222.71:44970',
    '200.54.42.3:8080',
    '196.54.47.140:80',
    '196.54.47.141:80',
    '196.54.47.146:80',
    '196.54.47.168:80',
    '196.54.47.17:80',
    '209.97.163.175:3128',
    '5.202.188.154:3128',
    '45.70.214.195:8080',
    '95.174.67.50:18080',
    '125.26.99.185:36525'
]
