# -*- coding: utf-8 -*-

import argparse
import json
import os
import traceback

from flask import Flask, request, render_template, g
from flask_mime import Mime
from werkzeug import SharedDataMiddleware

import operation as op
import log


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
    app.logger.info('read entries: %s', id_list)
    op.read_entries(id_list)
    return json.dumps({'message': 'ok'})


@mimetype('application/json')
@app.route('/entries/<int:id>', methods=['PATCH'])
def update_an_entry(id):
    changed = json.loads(request.data)
    app.logger.info('update an entry: %d %s', id, changed)
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
    app.logger.info('add a feed: %s', id, data)
    feed = op.add_a_feed(data.get('url'))
    return json.dumps(feed)


@mimetype('application/json')
@app.route('/feeds/<int:id>', methods=['PATCH'])
def update_a_feed(id):
    changed = json.loads(request.data)
    app.logger.info('update a feed: %d %s', id, changed)
    op.update_a_feed(id, changed)
    return json.dumps(changed)


@app.errorhandler(500)
def handle_error(e):
    app.logger.error(traceback.format_exc())
    raise


class WebApp(object):

    def __init__(self, hostname, port, database, logfile, debug=False):
        self.hostname = hostname
        self.port = port
        self.debug = debug

        app.logger.addHandler(log.get_handler(logfile))
        app.logger.setLevel(log.get_level(debug))

        app.secret_key = 'dummy_secret_key' if debug else os.urandom(24)
        app.wsgi_app = SharedDataMiddleware(
            app.wsgi_app,
            {'/': os.path.join(os.path.dirname(__file__), 'static')}
        )

        self.app = app

        self.app.logger.info(
            'crawler setup, hostname:%s port:%d log:%s debug:%s',
            hostname, port, logfile, debug
        )

        op.open_db(database)
        self.app.logger.info('db opened:%s', database)

    def start(self):
        app.logger.info('start webapp')
        app.run(self.hostname, self.port)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostname', default='0.0.0.0')
    parser.add_argument('--port', default=8080)
    parser.add_argument('--database', default='rss.db')
    parser.add_argument('--logfile', default='webapp.log')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    webapp = WebApp(
        args.hostname, args.port, args.database, args.logfile, args.debug
    )
    webapp.start()


if __name__ == '__main__':
    main()
