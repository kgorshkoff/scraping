# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import base64
import io

import pytesseract
from PIL import Image
from itemloaders.processors import MapCompose, Compose, TakeFirst
from scrapy import Item, Field, Selector


def validate_photo_url(value):
    return value if value[:2] != '//' else 'https:' + value


def get_prices(value):
    tag = Selector(text=value)
    result = {'name': tag.xpath('.//span//text()').extract_first(),
              'value': tag.xpath('//text()').extract_first().split()
              }
    result['value'] = float(''.join(result['value']))
    return result


def get_params(value):
    param_tag = Selector(text=value)
    key = param_tag.xpath('.//span[@class="item-params-label"]/text()').extract_first().split(':')[0]

    value = ' '.join(
        [itm.strip() for itm in param_tag.xpath('//li/text()').extract()
         if not itm.isspace()]
    )

    return key, value


def get_phone(value):
    b64_obj = io.BytesIO(base64.b64decode(value))
    image = Image.open(b64_obj)
    result = pytesseract.image_to_string(image).strip()

    return result


class AvitoItem(Item):
    title = Field(output_processor=TakeFirst())
    url = Field(output_processor=TakeFirst())
    images = Field(input_processor=MapCompose(validate_photo_url))
    prices = Field(input_processor=MapCompose(get_prices))
    address = Field(output_processor=MapCompose(str.strip))
    params = Field(output_processor=lambda x: dict(get_params(itm) for itm in x))
    phone = Field(output_processor=MapCompose(get_phone))


def parse_specs(value):
    selector = Selector(text=value)
    keys = selector.xpath('//div[@class="AdvertSpecs_label__2JHnS"]/text()').extract()
    values = selector.xpath('//a/text()|//div[@class="AdvertSpecs_data__xK2Qx"]/text()').extract()

    result = dict(zip(keys, values))
    return result

def parse_phone(value):
    result = value[4:]
    return result


class YoulaItem(Item):
    url = Field(output_processor=TakeFirst())
    title = Field(output_processor=TakeFirst())
    specs = Field(input_processor=MapCompose(parse_specs),
                  output_processor=TakeFirst())
    price = Field(input_processor=Compose(lambda x: ''.join(x[0].encode('ascii', 'ignore').decode())),
                  output_processor=TakeFirst())
    images = Field(input_processor=MapCompose(validate_photo_url))
    description = Field(output_processor=TakeFirst())
    seller = Field(output_processor=TakeFirst())
    phone = Field(input_processor=MapCompose(parse_phone), output_processor=TakeFirst())


class InstagramPostItem(Item):
    comments_disabled = Field()
    typename = Field()
    id = Field()
    edge_media_to_caption = Field()
    shortcode = Field()
    edge_media_to_comment = Field()
    taken_at_timestamp = Field()
    dimensions = Field()
    display_url = Field()
    edge_liked_by = Field()
    edge_media_preview_like = Field()
    owner = Field()
    thumbnail_src = Field()
    thumbnail_resources = Field()
    is_video = Field()
    accessibility_caption = Field()
    product_type = Field()
    video_view_count = Field()

class InstagramAuthorItem(Item):
    typename = Field()
    id = Field()
    expiring_at = Field()
    has_pride_media = Field()
    latest_reel_media = Field()
    seen = Field()
    user = Field()
    owner = Field()
