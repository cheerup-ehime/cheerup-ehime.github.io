#! /usr/bin/env python
# coding: utf-8

import urllib.request
from bs4 import BeautifulSoup
import sys
import re

def get_hinanjo_page(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find(id="wrap")
    title = body.h2.text
    print('---')
    print('title:' + title)
    print('---')
    content = body.p.get_text()
    array = content.split('\r\n')
    hinanjo = []
    jokyo = []
    hinansetai = []
    hinanninzu = []
    kousin = []
    for item in array:
        if re.search(r":(臨時)*避難所", item):
            s = item.split(' ')
            hinanjo.append(s[0].split(':')[0])
            jokyo.append(s[1])
        elif re.search(r"避難世帯数:", item):
            hinansetai.append(item.split(':')[1])
        elif re.search(r"避難人数:", item):
            hinanninzu.append(item.split(':')[1])
        elif re.search(r"\([0-9]+/[0-9]+/[0-9]+ [0-9]+:[0-9]+\)",item):
            kousin.append(item)
        else:
            pass

    print("|避難所名|状況|避難世帯数|避難人数|更新日|")
    print("|--|--|--|--|--|")
    for i in range(len(hinanjo)):
        print('|' + hinanjo[i] + '|' + jokyo[i] + '|' + hinansetai[i] + '|' + hinanninzu[i] + '|' + kousin[i] + '|')

def hinanjo(page_num = 1):
    url = 'http://ehime.force.com/PUB_VF_HinanjyoList'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html, "html.parser")
    for i in range(page_num):
        volunteer = soup.find_all("div", {"class": "volunteer"})[0]
        dls = volunteer.find_all("dl")
        dl = dls[i]
        get_hinanjo_page('http://ehime.force.com/' + dl.a.get('href'))

if __name__ == '__main__':
    args = sys.argv
    if len(args) == 2:
        hinanjo(int(args[1]))
    else:
        hinanjo()
