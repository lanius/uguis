# -*- coding: utf-8 -*-

from itertools import ifilterfalse

import feedparser

from model import database, open_database, Feed, Entry


db = database


def open_db(filepath):
    open_database(filepath)
    return db


# entry api for web app

def get_entries_as_dict(count, offset, priority, order):
    return [
        e.to_dict() for e in get_entries(count, offset, priority, order)
    ]


def get_entries(count, offset, priority, order):
    order = getattr(Entry.created_date, order)()
    return Entry.select().join(Feed).where(
        Feed.priority >= priority,
        Entry.is_read == False
    ).order_by(order).offset(offset).limit(count)


def read_entries(id_list):
    Entry.update(is_read=True).where(Entry.id << id_list).execute()


def update_an_entry(id, changed):
    e = Entry.get(id=id)
    for attr, value in changed.items():
        if attr in ['is_read', 'is_liked', 'is_disliked']:  # writable attr
            setattr(e, attr, value)
    e.save()


# feed api for web app

def get_feeds_as_dict():
    return [f.to_dict() for f in get_feeds()]


def get_feeds():
    return Feed.select().order_by(Feed.created_date.desc())


def feed_exists(url):
    return Feed.select().where(Feed.url == url).exists()


def add_a_feed(url):
    if feed_exists(url):
        raise Exception('feed already exists')  # todo: handle error
    feeddata = feedparser.parse(url)  # todo: handle error
    feed = Feed.create(url=feeddata.href, title=feeddata.feed.title)
    return feed.to_dict()


def update_a_feed(id, changed):
    f = Feed.get(id=id)
    for attr, value in changed.items():
        if attr in ['priority', 'is_disabled']:  # writable attr
            setattr(f, attr, value)
    f.save()


# entry api for crawler

def fetch_entries(feed):
    return [
        Entry(title=e.title, url=e.link, feed=feed)
        for e in feedparser.parse(feed.url).entries
    ]


def entry_exists(entry):
    return Entry.select().where(Entry.url == entry.url).exists()


def filter_new_entries(entries):
    return list(ifilterfalse(entry_exists, entries))


def add_an_entry(entry):
    # todo: user insert_many and where, when peewee versioned up
    with database.transaction():
        entry.save()


# feed api for crawler

def get_enabled_feeds():
    return list(Feed.select().where(
        Feed.is_disabled == False).order_by(Feed.created_date.desc()))
