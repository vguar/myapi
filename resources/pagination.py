from flask import url_for


def _get_range(start, limit, count):
    return '{start}-{stop}'.format(
        start=start, stop=min(start + limit - 1, count - 1))


def _get_content_range(start, stop, limit, count):
    return '{start}-{stop}/{count}'.format(
        start=start, stop=min(start + limit - 1, count - 1), count=count)


def _build_prev_url(start, limit, count, uuid, url_func):
    if start == 0:
        return ''
    prev_start = max(0, start - limit)
    prev_limit = start
    range = _get_range(prev_start, prev_limit, count)
    return url_for(url_func, id=uuid,
                   range=range , _external=True)


def _build_next_url(start, limit, count, uuid, url_func):
    if start + limit >= count:
        return ''
    next_start = start + limit
    range = _get_range(next_start, limit, count)
    return url_for(url_func, id=uuid,
                   range=range, _external=True)


def _build_first_url(limit, count, uuid, url_func):
    range = _get_range(0, limit, count)
    return url_for(url_func, id=uuid,
                   range=range, _external=True)


def _build_last_url(limit, count, uuid, url_func):
    start = 0 if count < limit else count - limit
    range = _get_range(start, limit, count)
    return url_for(url_func, id=uuid,
                   range=range, _external=True)


def _build_link(url_first, url_last, url_next, url_prev):
    link = '<{first}>; rel="first", <{last}>; rel="last"'.format(
        first=url_first, last=url_last)
    if url_prev:
        link += ', <{}>; rel="prev"'.format(url_prev)
    if url_next:
        link += ', <{}>; rel="next"'.format(url_next)
    return link


def _range_to_int(range_str):
    start, end = [int(i) for i in range_str.split("-")]
    limit = end - start + 1
    return start, end, limit


def get_paginated_list(result, uuid, range_str, url_func):
    start, end, limit = _range_to_int(range_str)
    header = {}
    body = {}
    return_code = 404
    if result is not None:
        count = len(result)
        if not limit or limit < 1:
            limit = count
        if start > count:
            return_code = 400
            pass
        else:
            return_code = 200 if limit >= (count - start) else 206
            body['results'] = result[start:start+limit]

            url_prev = _build_prev_url(start, limit, count, uuid, url_func)
            url_next = _build_next_url(start, limit, count, uuid, url_func)
            url_first = _build_first_url(limit, count, uuid, url_func)
            url_last = _build_last_url(limit, count, uuid, url_func)

            header['Content-Range'] = _get_content_range(
                start, min(start + limit - 1, count - 1), limit, count)
            header['Link'] = _build_link(
                url_first, url_last, url_next, url_prev)
            header['Content-Location'] = url_for(
                url_func, id=uuid,
                range='{}-{}'.format(start, start+limit), _external=True)
    return body, return_code, header