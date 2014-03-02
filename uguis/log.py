# -*- coding: utf-8 -*-

import logging
import logging.handlers


def get_level(debug=False):
    return logging.DEBUG if debug else logging.INFO


def get_handler(filepath):
    handler = logging.handlers.RotatingFileHandler(
        filepath,
        maxBytes=1024 * 1024 * 1024,  # 1GB
        backupCount=3
    )
    handler.setFormatter(logging.Formatter((
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    )))
    return handler


def get_logger(filepath, debug=False):
    logger = logging.getLogger()
    logger.addHandler(get_handler(filepath))
    logger.setLevel(get_level(debug))
    return logger
