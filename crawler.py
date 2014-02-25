# -*- coding: utf-8 -*-

import argparse
import datetime
import time
import traceback

import operation as op
import log


# todo: database connection management


def timestamp():
    return datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')


class Crawler(object):

    def __init__(self, interval, database, logfile, debug=False):
        self.interval = interval
        self.debug = debug
        self.logger = log.get_logger(logfile, debug)
        self.logger.info(
            'crawler setup, interval:%d log:%s debug:%s',
            interval, logfile, debug
        )

        op.open_db(database)
        self.logger.info('db opened:%s', database)

    def process_feed(self, feed):
        self.logger.debug('process feed %s', feed.title)
        entries = op.fetch_entries(feed)
        self.logger.debug('%d entries fetched', len(entries))

        if len(entries) == 0:
            self.logger.warn('feed is empty %d %s', feed.id, feed.title)

        return op.filter_new_entries(entries)

    def crawl(self):
        num_fetched_entries = 0
        for feed in op.get_enabled_feeds():
            entries = self.process_feed(feed)
            for entry in entries:
                op.add_an_entry(entry)
            num_fetched_entries += len(entries)
        self.logger.info('%d entries fetched', num_fetched_entries)

    def loop(self):
        while True:
            self.logger.info('crawling...')
            self.crawl()
            self.logger.info('sleep %d sec', self.interval)
            time.sleep(self.interval)

    def start(self):
        self.logger.info('start crawling')
        try:
            self.loop()
        except:
            self.logger.error(traceback.format_exc())
        self.logger.info('finish crawling')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', default=60 * 15)
    parser.add_argument('--database', default='rss.db')
    parser.add_argument('--logfile', default='crawler.log')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    crawler = Crawler(args.interval, args.database, args.logfile, args.debug)
    crawler.start()


if __name__ == '__main__':
    main()
