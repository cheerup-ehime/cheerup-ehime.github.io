#! /usr/bin/env python
# coding: utf-8


import urllib.request
from urllib.error import HTTPError
import datetime
import subprocess
import shlex
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

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        content = urllib.request.urlopen(req)
    except HTTPError:
        print('PDFがありません')
        return

    with open('data','wb') as output:
        output.write(content.read())
    
    cmd = "java -jar ./tabula-1.0.2-jar-with-dependencies.jar -o data.csv -p all -r ./data"

    args = shlex.split(cmd)
    p = subprocess.Popen(args)

    p.wait()

if __name__ == '__main__':
    get_higaijokyo_content()
