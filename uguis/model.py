# -*- coding: utf-8 -*-

import datetime
import os

from peewee import (
    PrimaryKeyField, ForeignKeyField, CharField, IntegerField, BooleanField,
    DateTimeField, Check, Model, SqliteDatabase
)


database = SqliteDatabase(None, threadlocals=True)


def open_database(filepath):
    if os.path.exists(filepath):
        database.init(filepath)
    else:
        database.init(filepath)
        create_table()


def close_database():
    database.close()


def create_table():
    Entry.create_table()
    Feed.create_table()


class BaseModel(Model):
    class Meta:
        database = database


class Feed(BaseModel):
    id = PrimaryKeyField()
    url = CharField(index=True)
    title = CharField()
    genre = CharField(default='other', index=True)
    priority = IntegerField(
        default=3, index=True,
        constraints=[Check('priority >= 0'), Check('priority <= 5')]
    )
    created_date = DateTimeField(default=datetime.datetime.now, index=True)
    is_disabled = BooleanField(default=False, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'genre': self.genre,
            'priority': self.priority,
            'is_disabled': self.is_disabled,
        }


class Entry(BaseModel):
    id = PrimaryKeyField(index=True)
    url = CharField(unique=True, index=True)
    title = CharField()
    created_date = DateTimeField(default=datetime.datetime.now, index=True)
    is_read = BooleanField(default=False, index=True)
    is_liked = BooleanField(default=False, index=True)
    is_disliked = BooleanField(default=False, index=True)
    feed = ForeignKeyField(Feed)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'created_date': self.created_date.strftime('%Y/%m/%d'),
            'is_read': self.is_read,
            'is_liked': self.is_liked,
            'is_disliked': self.is_disliked,
            'feed': self.feed.title
        }
