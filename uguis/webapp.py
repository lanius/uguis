# -*- coding: utf-8 -*-

import argparse
import json
import os
import traceback

from flask import Flask, request, render_template, g
from flask_mime import Mime
from werkzeug import SharedDataMiddleware
import logbook

import operation as op


logbook.set_datetime_format('local')
logger = logbook.Logger('WebApp')

app = Flask(__name__)
mimetype = Mime(app)


@app.before_request
def before_request():
    g.db = op.db
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@mimetype('text/html')
@app.route('/')
@app.route('/entries/')
@app.route('/entries/<path:path>')
@app.route('/feeds/<path:path>')
def index(path=None):
    return render_template('index.html')


@mimetype('application/json')
@app.route('/entries/')
def get_entries():
    count = request.args.get('count', type=int, default=30)
    offset = request.args.get('offset', type=int, default=0)
    priority = request.args.get('priority', type=int, default=5)
    order = request.args.get('order', default='desc')
    return json.dumps(op.get_entries_as_dict(count, offset, priority, order))


@mimetype('application/json')
@app.route('/entries/read', methods=['POST'])
def read_entries():
    id_list = json.loads(request.form['id_list'])
    logger.info('read entries: {0}', id_list)
    op.read_entries(id_list)
    return json.dumps({'message': 'ok'})


@mimetype('application/json')
@app.route('/entries/<int:id>', methods=['PATCH'])
def update_an_entry(id):
    changed = json.loads(request.data)
    logger.info('update an entry: {0} {1}', id, changed)
    op.update_an_entry(id, changed)
    return json.dumps(changed)


@mimetype('application/json')
@app.route('/feeds/')
def get_feeds():
    return json.dumps(op.get_feeds_as_dict())


@mimetype('application/json')
@app.route('/feeds/', methods=['POST'])
def add_a_feed():
    data = json.loads(request.data)
    logger.info('add a feed: {0} {1}', id, data)
    feed = op.add_a_feed(data.get('url'))
    return json.dumps(feed)


@mimetype('application/json')
@app.route('/feeds/<int:id>', methods=['PATCH'])
def update_a_feed(id):
    changed = json.loads(request.data)
    logger.info('update a feed: {0} {1}', id, changed)
    op.update_a_feed(id, changed)
    return json.dumps(changed)


@app.errorhandler(500)
def handle_error(e):
    logger.error(traceback.format_exc())
    raise


class WebApp(object):

    def __init__(self, hostname, port, database, debug=False):
        self.hostname = hostname
        self.port = port
        self.debug = debug

        app.debug = debug
        app.secret_key = 'dummy_secret_key' if debug else os.urandom(24)
        app.wsgi_app = SharedDataMiddleware(
            app.wsgi_app,
            {'/': os.path.join(os.path.dirname(__file__), 'static')}
        )

        op.open_db(database)

        logger.info(
            'crawler setup: hostname {0}, port {1}, db {2}, debug {3}',
            hostname, port, database, debug
        )

    def start(self):
        logger.info('start webapp')
        app.run(self.hostname, self.port)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostname', default='0.0.0.0')
    parser.add_argument('--port', default=8080)
    parser.add_argument('--database', default='rss.db')
    parser.add_argument('--logfile', default='webapp.log')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    log_handler = logbook.RotatingFileHandler(
        args.logfile,
        level=logbook.DEBUG if args.debug else logbook.INFO
    )
    with log_handler.applicationbound():
        webapp = WebApp(args.hostname, args.port, args.database, args.debug)
        webapp.start()


if __name__ == '__main__':
    main()
