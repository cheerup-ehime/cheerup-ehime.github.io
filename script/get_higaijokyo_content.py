#! /usr/bin/env python
# coding: utf-8


import urllib.request
from urllib.error import HTTPError
import datetime
import subprocess
import shlex
from io import StringIO

def get_days():
    today = datetime.date.today()
    begin = datetime.date(2018, 7, 30)
    days = (today - begin).days + 63
    if (datetime.datetime.now().hour < 12):
        days -= 1
    return days
    
def fetch_content(days):
    url = 'http://www.pref.ehime.jp/h12200/documents/higaijokyo' + str(days) + '.pdf'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        return urllib.request.urlopen(req)
    except HTTPError:
        print('第{}報のPDFがありません'.format(days))

    return None


def get_higaijokyo_content():
    
    days = get_days()

    for ver in range(days+1)[::-1]:
        content = fetch_content(ver)
        if content != None:
            print('第{}報のPDFを取得！'.format(days))
            break

    if content == None:
        print('レポートが入手できませんでした')
        return

    with open('data','wb') as output:
        output.write(content.read())
    
    cmd = "java -jar ./tabula-1.0.2-jar-with-dependencies.jar -o data.csv -p all -r ./data"

    args = shlex.split(cmd)
    p = subprocess.Popen(args)

    p.wait()

if __name__ == '__main__':
    get_higaijokyo_content()
