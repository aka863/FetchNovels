#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from novel import single, utils, config

BASE_URL = 'http://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid={}'


class Cool18Tool(utils.Tool):

    def __init__(self):
        super().__init__(remove_span=False)
        self.remove_extras.append(
            re.compile(r'<.*?bodyend.*?>.*')
        )


class Cool18(single.SingleNovel):

    def __init__(self, tid):
        super().__init__(utils.base_to_url(BASE_URL, tid), 'pre',
                         title_type=single.TitleType.meta,
                         title_sel=('name', 'Description'),
                         tid=tid)
        self.tool = Cool18Tool
        self.encoding = config.GB


if __name__ == '__main__':
    tids = []
    with open("tids_cool18_to_dl") as f:
        for line in f:
            tid = line.strip() 
            if tid != '':
                tids.append(tid)
    tids.sort()
    titles  = []
    contents = []
    for tid in tids:
        cool18 = Cool18(tid)
        cool18.run()
        title = cool18.get_title()
        print(title)
        titles.append(title)
        contents.append(cool18.get_content())
    filename = titles[-1] + '.txt'
    print(filename)
    with open('mhwa.txt', 'w') as fp:
        for title,content in zip(titles,contents):
            fp.write(title)
            fp.write('\n\n\n\n')
            fp.write(content)
            fp.write('\n')
        

