#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from pyquery import PyQuery

from novel import serial, utils, config

BASE_URL = 'http://www.danmei123.cc/{}/'


class Danmei123(serial.SerialNovel):

    def __init__(self, tid):
        super().__init__(utils.base_to_url(BASE_URL, tid), '.box_box',
                         intro_sel='.j_box .words p',
                         chap_type=serial.ChapterType.path,
                         chap_sel='.list_box li',
                         tid=tid)
        self.encoding = config.GB

    def get_title_and_author(self):
        st = self.doc('meta').filter(
            lambda i, e: PyQuery(e).attr('name') == 'description'
        ).attr('content')
        pat = re.compile(r'(.*)的新书(.*)最新章节.*')
        author, name = re.match(pat, st).groups()

        return name, author
