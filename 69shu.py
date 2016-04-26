#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
from urllib.parse import urljoin
from pyquery import PyQuery as pq

from novel import serial, utils

BASE_URL = 'http://www.69shu.com/%s/'
INTRO_URL = 'http://www.69shu.com/modules/article/jianjie.php?id=%s'
ENCODING = 'GB18030'


class Shu69(serial.Novel):

    def __init__(self, tid, proxies=None):
        super().__init__(BASE_URL % tid, INTRO_URL % tid,
                         '.jianjie', '.yd_text2',
                         serial.HEADERS, proxies, ENCODING)

    def get_title_and_author(self):
        st = self.doc('meta').filter(
            lambda i, e: pq(e).attr('name') == 'keywords'
        ).attr('content')
        name = re.match(r'(.*?),.*', st).group(1)
        author = self.doc('.mu_beizhu').eq(0)('a').eq(1).text()
        return name, author

    @property
    def chapter_list(self):
        clist = self.doc('.mulu_list').eq(1)('li').map(
            lambda i, e: (i,
                          urljoin(utils.get_base_url(self.url),
                                  pq(e)('a').attr('href')),
                          pq(e).text())
        ).filter(
            lambda i, e: e[1] is not None
        )
        return clist


def main():
    tids = sys.argv[1:]
    print(tids)
    if len(tids) == 0:
        print('No specific tid!')
        sys.exit(1)
    for tid in tids:
        yq = Shu69(tid, serial.GOAGENT)
        yq.dump()


if __name__ == '__main__':
    main()