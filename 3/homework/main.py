from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Author, Post, Tag, Hub
from crawler import GBBlogParser


class SQLManager:
    def __init__(self):
        self.engine = create_engine('sqlite:///habr_top.db')
        Base.metadata.create_all(self.engine)
        self.session_db = sessionmaker(bind=self.engine)
        self.session = self.session_db()

    def get_or_create(self, model, **kwargs):
        instance = self.session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            self.session.add(instance)
            self.session.commit()
            return instance

    def save(self, arr):
        for itm in arr:
            post_tags = itm.pop('tags')
            post_hubs = itm.pop('hubs')
            post_author = itm.pop('author')

            args = {
                'url': itm['url'],
                'title': itm['title'],
                'author_id': self.get_or_create(Author, **post_author[0]).id,
            }

            post = self.get_or_create(Post, **args)

            for tag in post_tags:
                obj = self.get_or_create(Tag, **tag)
                post.tag.append(obj)
            for hub in post_hubs:
                obj = self.get_or_create(Hub, **hub)
                post.hub.append(obj)

            self.session.commit()

        self.session.close()


if __name__ == '__main__':
    parser = GBBlogParser()
    parser.parse_rows()
    parser.post_page_parse()

    sql = SQLManager()
    sql.save(parser.post_data)
