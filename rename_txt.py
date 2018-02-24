#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import glob
import os
from  novel.tools import cn2int

os.chdir("zhou")
txt_names = glob.glob('*.txt')
#print(txt_names)

p = re.compile('（.*?）')

for f_name in txt_names:
    m = p.search(f_name)
    if m:
        print(f_name)
        #print(m)
        cn_num = m.group()
        cn_num = cn_num[1:-1]
        if not cn_num[0].isdigit():
            int_num = cn2int.chinese_to_arabic(cn_num)
            f_name_pre = '{:0>3}'.format(int_num)
            print(f_name_pre)
            os.rename(f_name,f_name_pre + f_name)