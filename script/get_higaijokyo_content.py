#! /usr/bin/env python
# coding: utf-8

# pip install pdfminer.six が必要です。

import urllib.request
from urllib.error import HTTPError
import datetime

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams, LTRect, LTTextBoxHorizontal
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from io import StringIO


def generate_url():
    today = datetime.date.today()
    begin = datetime.date(2018, 7, 30)
    days = (today - begin).days + 63
    if (datetime.datetime.now().hour < 12):
        days -= 1

    return 'http://www.pref.ehime.jp/h12200/documents/higaijokyo' + str(days) + '.pdf'

def get_higaijokyo_content():
    url = generate_url()
    rsrcmgr = PDFResourceManager()

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        content = urllib.request.urlopen(req)
    except HTTPError:
        print('PDFがありません')
        return

    with open('data','wb') as output:
        output.write(content.read())
    fp = open('data', 'rb')
    laparams = LAParams()
    device =  PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    for page in PDFPage.get_pages(fp, pagenos=None, maxpages=0, password=None,caching=True, check_extractable=True):
        interpreter.process_page(page)
        layout = device.get_result()
        prev_node = None
        str_line = ''
        for node in layout:
            if isinstance(node, LTTextBoxHorizontal):
                if (prev_node and prev_node.y1 == node.y1):
                    str_line += ','
                    str_line += node.get_text().strip()
                else:
                    print(str_line)
                    str_line = node.get_text().strip()
                prev_node = node

    fp.close()
    device.close()

if __name__ == '__main__':
    get_higaijokyo_content()
