# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
'''
{
'title': str,
'url': str,
'photo': List[str],
'price': Dict[str, str],
'address': str,
'params': List[Dict[str, str]],
'phone': str
 }
 '''


class GbdmItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    title = Field()
    url = Field()
    photo = Field()
    price = Field()
    address = Field()
    params = Field()
    phone = Field
