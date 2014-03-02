# -*- coding: utf-8 -*-

import os
import random
import shutil
import sys
import tempfile

import pytest


def _generate_feeds():
    from model import database as db, Feed
    feeds = [
        Feed(
            url='http://test.example.com/feed/{0}'.format(i),
            title='feed title {0}'.format(i),
            priority=random.randint(0, 5),
            is_disabled=random.choice([True, False])
        ) for i in range(random.randint(10, 100))
    ]
    with db.transaction():
        for f in feeds:
            f.save()
    return feeds


def _generate_entries(feeds):
    from model import database as db, Entry
    if not feeds:
        return []
    entries = [
        Entry(
            url='http://test.example.com/entry/{0}'.format(i),
            title='entry title {0}'.format(i),
            is_read=random.choice([True, False]),
            feed=random.choice(feeds)
        ) for i in range(random.randint(100, 1000))
    ]
    with db.transaction():
        for e in entries:
            e.save()
    return entries


def pytest_configure(config):
    sys._path = sys.path
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.join(PROJECT_ROOT, 'uguis'))


def pytest_unconfigure(config):
    sys.path = sys._path
    del sys._path


def pytest_runtest_setup(item):
    seed = random.randint(0, 1000)
    random.seed(seed)
    print('seed', seed)


@pytest.fixture()
def database(request):
    from model import open_database, close_database
    dirpath = tempfile.mkdtemp()
    open_database(os.path.join(dirpath, 'testing.db'))
    feeds = _generate_feeds()
    _generate_entries(feeds)

    def fin():
        close_database()
        shutil.rmtree(dirpath)
    request.addfinalizer(fin)
