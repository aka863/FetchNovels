#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Some help functions
"""

import collections
import os
import re
import sqlite3
import string
import sys
from multiprocessing.dummy import Pool
from random import randrange
from urllib.parse import urlparse, urlunparse

from .const import UAS
from .error import Error


class Tool(object):
    """
    A class to remove needless tags and strings
    """

    def __init__(self):
        self._remove_a = re.compile(r'<a.*?>.*?</a>', re.I)
        self._remove_div = re.compile(r'<div.*?>.*?</div>',
                                      re.I | re.S)
        self._remove_span = re.compile(r'<span.*?>.*?</span>',
                                       re.I | re.S)
        self._remove_script = re.compile(r'<script.*?>.*?</script>',
                                         re.I | re.S)
        self._replace_br = re.compile(r'<br\s*/\s*>|</\s*br>', re.I)
        self._replace_p = re.compile(r'</?p>', re.I)
        self._replace_h = re.compile(r'</h\d*?>')
        self._replace_xa0 = re.compile(r'\xa0')
        self._replace_u3000 = re.compile(r'\u3000')
        self._remove_ufeff = re.compile(r'\ufeff')
        self._remove_r = re.compile(r'&#13;|\r')
        self._replace_gt = re.compile(r'&gt;')
        self._replace_lt = re.compile(r'&lt;')
        self.replace_extras = []
        self.remove_extras = []
        self._remove_ot = re.compile(r'<.*?>')

    def replace(self, text):
        """
        Replace and remove needless strings

        Some default options are pre-defined.
        You can add custom options to replace_extras or remove_extras.
        """
        text = re.sub(self._remove_a, '', text)
        text = re.sub(self._remove_div, '', text)
        text = re.sub(self._remove_script, '', text)
        text = re.sub(self._replace_br, '\n', text)
        text = re.sub(self._replace_p, '\n', text)
        text = re.sub(self._replace_h, '\n\n', text)
        text = re.sub(self._replace_xa0, ' ', text)
        text = re.sub(self._replace_u3000, '  ', text)
        text = re.sub(self._remove_ufeff, '', text)
        text = re.sub(self._remove_r, '', text)
        text = re.sub(self._replace_gt, '>', text)
        text = re.sub(self._replace_lt, '<', text)
        for s, d in self.replace_extras:
            text = re.sub(s, d, text)
        for pat in self.remove_extras:
            text = re.sub(pat, '', text)
        text = re.sub(self._remove_ot, '', text)
        return text

    def refine(self, text):
        """
        Get a better printed text

        Replace and remove needless strings, and then
        remove too many continuous newlines.
        """
        text = self.replace(text)

        text = re.sub(r'\n\s+\n', '\n\n', text)
        text = re.sub(r'[ \t]+\n', '\n', text)

        return text.strip()


def fix_order(i):
    """
    Fix the order of list item.

    Sometimes we get a list of order
    [0<2>, 1<1>, 2<0>, 3<5>, 4<4>, 5<3>, ...],
    and what we need is [2<0>, 1<1>, 0<2>, 5<3>, 4<4>, 3<5>, ...].
    """
    if i % 3 == 0:
        return i + 2
    elif i % 3 == 2:
        return i - 2
    else:
        return i


def count(iterable):
    """
    Count the number of items that `iterable` yields

    Equivalent to the expression

    ::
      len(iterable),

    ... but it also works for iterables that do not support ``len()``.

    ::

      >>> import cardinality
      >>> cardinality.count([1, 2, 3])
      3
      >>> cardinality.count(i for i in range(500))
      500
      >>> def gen():
      ...     yield 'hello'
      ...     yield 'world'
      >>> cardinality.count(gen())
      2

    Get from https://github.com/wbolster/cardinality/blob/master/cardinality.py
    """
    if hasattr(iterable, '__len__'):
        return len(iterable)

    d = collections.deque(enumerate(iterable, 1), maxlen=1)
    return d[0][0] if d else 0


def get_field_count(format_string):
    fmt = string.Formatter()
    return count(t for t in fmt.parse(format_string) if t[1] is not None)


def base_to_url(base_url, tid):
    """
    Get the url from template

    The base_url must have two replacement fields.
    The second field is just filled with the tid,
    while the first field with the tid which has been
    stripped the last three number.
    """
    field_count = get_field_count(base_url)
    if field_count == 1:
        return base_url.format(tid)
    elif field_count == 2:
        return base_url.format(int(tid) // 1000, tid)
    else:
        raise Error('Function base_to_url with {} replacement fields is not defined!'.format(field_count))


def get_base_url(url):
    """
    Transform a full url into its base url

    For example:

    ::
      >>> get_base_url('http://example.com/text/file?var=f')
      'http://example.com'
    """
    result = urlparse(url)
    base_url = urlunparse((result.scheme, result.netloc, '', '', '', ''))
    return base_url


def get_filename(title, author=None, overwrite=True):
    if author:
        base = '《{}》{}'.format(title, author)
    else:
        base = title

    filename = '{}.txt'.format(base)
    if not overwrite:
        if os.path.exists(filename):
            for i in count(1):
                filename = '{}({:d}).txt'.format(base, i)
                if not os.path.exists(filename):
                    break
    return filename


def get_headers():
    ua = randrange(len(UAS))
    headers = {'User-Agent': ua}
    return headers


def in_main(NovelClass, proxies=None, overwrite=True):
    """
    A pre-defined main function

    Get tids for command line parameters, and save content in each files.
    """
    tids = sys.argv[1:]
    print(tids)
    if len(tids) == 0:
        print('No specific tid!')
        sys.exit(1)

    def dump(tid):
        nov = NovelClass(tid)
        nov.proxies = proxies
        nov.dump(overwrite=overwrite)

    num = len(tids)
    with Pool(num) as p:
        p.map(dump, tids)


class SqlHelper():

    def __init__(self, db):
        self.conn = sqlite3.connect(db, check_same_thread=False)

    def create_table(self, sql):
        try:
            self.conn.execute(sql)
        except Exception as e:
            print('create table: {}'.format(e))

    def insert_data(self, sql, parameters=None):
        try:
            self.conn.execute(sql, parameters)
            self.conn.commit()
        except Exception as e:
            print('insert data: {}'.format(e))

    def insert_many_data(self, sql, parameters=None):
        try:
            self.conn.executemany(sql, parameters)
            self.conn.commit()
        except Exception as e:
            print('insert many data: {}'.format(e))

    def update_data(self, sql, parameters=None):
        try:
            self.conn.execute(sql, parameters)
            self.conn.commit()
        except Exception as e:
            print('update data: {}'.format(e))

    def select_data(self, sql, parameters=None):
        try:
            self.cursor = self.conn.execute(sql, parameters or ())
            return self.cursor
        except Exception as e:
            print('select data: {}'.format(e))

    def close(self):
        try:
            self.conn.close()
        except Exception as e:
            print('close connection: {}'.format(e))
