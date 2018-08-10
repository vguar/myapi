from __future__ import absolute_import
import logging
from os import getenv
from sys import exit

from celery import Celery

LOG = logging.getLogger('amazingresources')

redis_port = getenv('REDIS_PORT', '6379')
redis_db = getenv('REDIS_DB', '1')
redis_host = getenv('REDIS_HOST', '127.0.0.1')

redis_url = 'redis://{host}:{port}/{db}'.format(
    host=redis_host, port=redis_port, db=redis_db)

CONSUMER_APP = Celery('amazingresources', include=['consumer.tasks'])
CONSUMER_APP.conf.broker_url = redis_url
CONSUMER_APP.conf.result_backend = redis_url
CONSUMER_APP.conf.task_track_started = True
