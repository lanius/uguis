# -*- coding: utf-8 -*-

import argparse
import time
import traceback

import logbook

import operation as op


# todo: database connection management


logbook.set_datetime_format('local')
logger = logbook.Logger('Crawler')


class Crawler(object):

    def __init__(self, interval, database, debug=False):
        self.interval = interval
        self.debug = debug

        op.open_db(database)

        logger.info(
            'crawler setup: interval {0}, db {1}, debug {2}',
            interval, database, debug
        )

    def process_feed(self, feed):
        logger.debug('process feed: {0}', feed.title)
        entries = op.fetch_entries(feed)
        logger.debug('{0} entries fetched', len(entries))

        if len(entries) == 0:
            logger.warn('feed is empty: {0} {1}', feed.id, feed.title)

        return op.filter_new_entries(entries)

    def crawl(self):
        num_fetched_entries = 0
        for feed in op.get_enabled_feeds():
            entries = self.process_feed(feed)
            for entry in entries:
                op.add_entry(entry)
            num_fetched_entries += len(entries)
        logger.info('{0} entries fetched', num_fetched_entries)

    def loop(self):
        while True:
            logger.info('crawling...')
            self.crawl()
            logger.info('sleep {0} sec', self.interval)
            time.sleep(self.interval)

    def start(self):
        logger.info('start crawling')
        try:
            self.loop()
        except:
            logger.error(traceback.format_exc())
        logger.info('finish crawling')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', default=60 * 15, type=float)
    parser.add_argument('--database', default='rss.db')
    parser.add_argument('--logfile', default='crawler.log')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    log_handler = logbook.RotatingFileHandler(
        args.logfile,
        level=logbook.DEBUG if args.debug else logbook.INFO
    )
    with log_handler.applicationbound():
        crawler = Crawler(args.interval, args.database, args.debug)
        crawler.start()


if __name__ == '__main__':
    main()
