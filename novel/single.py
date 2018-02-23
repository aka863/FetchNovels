#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum

from pyquery import PyQuery

from novel.base import SinglePage

from novel.utils import get_filename, get_base_url


class TitleType(Enum):
    selector = 1
    meta = 2


class SingleNovel(SinglePage):

    def __init__(self, url, selector=None,
                 title_type=None, title_sel=None,
                 tid=None):
        super().__init__(url, selector,
                         tid=tid)
        self.title_type = title_type
        self.title_sel = title_sel

    def run(self, refresh=False):
        super().run(refresh=refresh)
        print(self.title)

    def get_title(self):
        if  not self.title_sel:
            raise NotImplementedError('get_title')
        if  self.title_type == TitleType.selector:
            return self.refine(self.doc(self.title_sel).html())
        elif self.title_type == TitleType.meta:
            return self.doc('meta').filter(
                lambda i, e:
                PyQuery(e).attr(self.title_sel[0]) == self.title_sel[1]
            ).attr('content').strip()
        else:
            raise NameError('title_type')

    def get_content(self):
        if not self.selector:
            raise NotImplementedError('get_content')
        content = '\n\n\n\n'.join(
            self.doc(self.selector).map(
                lambda i, e: self.refine(PyQuery(e).html())
            )
        )
        return content

    def dump(self):
        filename = get_filename(self.title, overwrite=self.overwrite)
        print(filename)
        content = self.content
        with open(filename, 'w') as fp:
            fp.write(self.title)
            fp.write('\n\n\n\n')
            fp.write(content)
            fp.write('\n')

    def dump_and_close(self):
        self.run()
        self.dump()

