from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

"""
one to one - один к одному
one to many - один к многому -> many to one
many to many - многое к многому
"""

tag_post = Table('tag_post', Base.metadata,
                 Column('post_id', Integer, ForeignKey('post.id')),
                 Column('tag_id', Integer, ForeignKey('tag.id'))
                 )

hub_post = Table('hub_post', Base.metadata,
                 Column('post_id', Integer, ForeignKey('post.id')),
                 Column('hub_id', Integer, ForeignKey('hub.id'))
                 )

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, unique=False, nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author', back_populates='post')
    tag = relationship('Tag', secondary=tag_post, back_populates='post')
    hub = relationship('Hub', secondary=hub_post, back_populates='post')

    def __init__(self, url: str, title: str, author_id=None, tags=[], hubs=[]):
        self.url = url
        self.title = title
        self.author_id = author_id
        self.tag.extend(tags)
        self.hub.extend(hubs)


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False, nullable=False)
    post = relationship('Post', back_populates='author')

    def __init__(self, url: str, name: str, posts=[]):
        self.url = url
        self.name = name
        self.post.extend(posts)


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False, nullable=False)
    post = relationship('Post', secondary=tag_post, back_populates='tag')

    def __init__(self, url: str, name: str, posts=[]):
        self.url = url
        self.name = name
        self.post.extends(posts)


class Hub(Base):
    __tablename__ = 'hub'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False, nullable=False)
    post = relationship('Post', secondary=hub_post, back_populates='hub')

    def __init__(self, url: str, name: str, posts=[]):
        self.url = url
        self.name = name
        self.post.extends(posts)
