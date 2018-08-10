import pytest

from celery.result import AsyncResult

from consumer.celery import CONSUMER_APP
from consumer import tasks


class InvalidTestType(Exception):

    def __init__(self, test_type):
        msg = 'Invalid test type {}'.format(test_type)
        super(InvalidTestType, self).__init__(msg)


def get_unit_result(task_name='post', kwargs={}):
    task = getattr(tasks, task_name)
    return task(**kwargs)


def get_functional_result(task_name='post', kwargs={}):
    async_result = CONSUMER_APP.send_task(
        'amazingresources.' + task_name,
        kwargs=kwargs,
        queue='amazingresources')
    return async_result.get()


def mark_test_class(test_type):
    def decorator(cls):
        if test_type == 'unit':
            cls = pytest.mark.unit(cls)
            cls.get_result = staticmethod(get_unit_result)
        elif test_type == 'functional':
            cls = pytest.mark.functional(cls)
            cls.get_result = staticmethod(get_functional_result)
        else:
            raise InvalidTestType(test_type)
        cls.test_type = test_type
        return cls
    return decorator
