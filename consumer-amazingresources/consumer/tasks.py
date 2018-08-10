from __future__ import absolute_import
import time

from celery.result import AsyncResult
from consumer.celery import CONSUMER_APP
from consumer.utils import get_logger


LOG = get_logger()


@CONSUMER_APP.task(name='amazingresources.post', bind=True)
def post(self, *args, **kwargs):
    LOG.debug(
        'Received post task with args {} and kwargs {}\n'.format(args, kwargs))
    try:
        output = {
            'results': [{
                'id': 'awesome-id',
                'description': kwargs['description'],
            }],
            'success': True,
            'error_msg': None,
        }
        time.sleep(15)
        return output
    except KeyError:
        return {
            'success': False,
            'error_msg': 'No description provided',
        }


@CONSUMER_APP.task(name='amazingresources.test', bind=True)
def test(self, *args, **kwargs):
    LOG.debug(
        'Received test task with args {} and kwargs {}\n'.format(args, kwargs))
    body = {
        'args': args,
        'kwargs': kwargs,
    }
    return {
        'results': body,
        'success': True,
        'error_msg': None,
    }
