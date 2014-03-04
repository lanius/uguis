# -*- coding: utf-8 -*-

import pytest
import mock


usefixtures = pytest.mark.usefixtures
parametrize = pytest.mark.parametrize


@pytest.fixture
def operation():
    import operation
    return operation


@pytest.fixture
def model():
    import model
    return model


@usefixtures('database')
@parametrize('count, offset, priority, order', [
    (10, 0, 0, 'asc')
])
def test_get_entries_as_dict(operation, count, offset, priority, order):
    dicts = operation.get_entries_as_dict(count, offset, priority, order)
    assert all(map(lambda d: isinstance(d, dict), dicts))


@usefixtures('database')
@parametrize('count, offset, priority, order', [
    (5, 0, 0, 'asc'),
    (5, 5, 0, 'asc'),
    (5, 0, 5, 'asc'),
    (5, 0, 0, 'desc')
])
def test_get_entries(operation, model, count, offset, priority, order):
    entries = operation.get_entries(count, offset, priority, order)

    # count
    actual_num_entries = len(list(
        model.Entry.select().join(model.Feed).where(
            model.Feed.priority >= priority,
            model.Entry.is_read == False
        ).offset(offset).limit(count)
    ))
    if actual_num_entries < count:
        assert len(entries) == actual_num_entries
    else:
        assert len(entries) == count

    # offset
    entries_from_head = operation.get_entries(count, 0, priority, order)
    offset_entries = entries_from_head[:offset]
    assert all(map(lambda e: e not in entries, offset_entries))

    # priority
    assert all(map(lambda e: e.feed.priority >= priority, entries))

    # order
    if order == 'asc':
        cmp_func = lambda t: t[0].created_date <= t[1].created_date
    else:  # 'desc'
        cmp_func = lambda t: t[0].created_date >= t[1].created_date
    assert all(map(cmp_func, zip(entries, entries[1:])))

    # is_read
    assert all(map(lambda e: e.is_read is False, entries))


@usefixtures('database')
def test_read_entries(operation, model):
    unread_entries = list(
        model.Entry.select().where(model.Entry.is_read == False)
    )

    if unread_entries:
        read_tagets = unread_entries[:len(unread_entries)/2]
    else:
        read_tagets = []
    target_id_list = [e.id for e in read_tagets]

    operation.read_entries(target_id_list)

    # all target entries are changed to be read
    assert all(map(
        lambda e: e.is_read is True,
        model.Entry.select().where(model.Entry.id << target_id_list)
    ))

    # number of read entries
    assert model.Entry.select().where(
        model.Entry.is_read == False
    ).count() == len(unread_entries) - len(read_tagets)


@usefixtures('database')
@parametrize('changed', [
    ({'is_read': True, 'is_liked': True, 'is_disliked': True}),
    ({'is_read': False, 'is_liked': False, 'is_disliked': False})
])
def test_update_an_entry(operation, model, changed):
    entry = model.Entry.select().first()
    if entry:
        operation.update_an_entry(entry.id, changed)
        assert all([
            getattr(
                model.Entry.get(id=entry.id), k
            ) == v for k, v in changed.items()
        ])


@usefixtures('database')
def test_get_feeds_as_dict(operation):
    feed_dicts = operation.get_feeds_as_dict()
    assert all(map(lambda f: isinstance(f, dict), feed_dicts))


@usefixtures('database')
def test_get_feeds(operation, model):
    feeds = operation.get_feeds()

    # number of all feeds
    assert len(feeds) == model.Feed.select().count()

    # feeds order
    assert all(map(
        lambda t: t[0].created_date >= t[1].created_date,
        zip(feeds, feeds[1:])
    ))


@usefixtures('database')
def test_feed_exists(operation, model):
    feed = model.Feed.select().first()
    if feed:
        assert operation.feed_exists(feed.url)
    assert not operation.feed_exists('http://notexists.example.com/feed')


@usefixtures('database')
def test_add_a_feed(operation, model):
    num_feeds = model.Feed.select().count()
    with mock.patch('feedparser.parse') as m:
        url = 'http://new.example.com/feed'
        operation.add_a_feed(url)
        assert m.call_args[0][0] == url
    assert model.Feed.select().count() == num_feeds + 1


@usefixtures('database')
@parametrize('changed', [
    ({'priority': 0, 'is_disabled': True}),
    ({'priority': 5, 'is_disabled': False})
])
def test_update_a_feed(operation, model, changed):
    feed = model.Feed.select().first()
    operation.update_a_feed(feed.id, changed)
    assert all([
        getattr(
            model.Feed.get(id=feed.id), k
        ) == v for k, v in changed.items()
    ])


@usefixtures('database')
def test_fetch_entries(operation, model):
    raw_feed = mock.Mock()
    raw_feed.entries = [mock.Mock()]

    feed = model.Feed(title='test', url='http://new.example.com/feed')

    with mock.patch('feedparser.parse', return_value=raw_feed) as m:
        entries = operation.fetch_entries(feed)
        assert m.call_args[0][0] == feed.url

    entry = entries[0]
    assert entry.title == raw_feed.entries[0].title
    assert entry.url == raw_feed.entries[0].link
    assert entry.feed is feed


@usefixtures('database')
def test_entry_exists(operation, model):
    feed = model.Feed.select().first()
    if feed:
        entry = model.Entry(
            title='test',
            url='http://new.example.com/entry',
            feed=feed
        )
        assert not operation.entry_exists(entry)
        entry.save()
        assert operation.entry_exists(entry)


@usefixtures('database')
def test_filter_new_entries(operation, model):
    entries = list(model.Entry.select())

    feed = model.Feed.select().first()
    if feed:
        new_entries = [model.Entry(
            title='test',
            url='http://new.example.com/entry/{0}'.format(i),
            feed=feed
        ) for i in range(10)]
        entries.extend(new_entries)
    else:
        new_entries = []

    filtered = operation.filter_new_entries(entries)
    assert len(filtered) == len(new_entries)
    assert all(map(lambda e: e in filtered, new_entries))


@usefixtures('database')
def test_add_an_entry(operation, model):
    num_entries = model.Entry.select().count()

    feed = model.Feed.select().first()
    operation.add_an_entry(model.Entry(
        title='test',
        url='http://new.example.com/entry',
        feed=feed
    ))
    assert model.Entry.select().count() == num_entries + 1


@usefixtures('database')
def test_get_enabled_feeds(operation):
    feeds = operation.get_enabled_feeds()
    assert all(map(lambda f: f.is_disabled == False, feeds))
