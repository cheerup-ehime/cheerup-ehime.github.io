#! /usr/bin/env python
# coding: utf-8
import click
from datetime import datetime as dt

template = '''---
title: 【{title}】
excerpt: {excerpt}
category:
    - {category}
date: {date}
last_modified_at: {date} 
sidemenu:
    nav: posts-menu
---

**情報元**:[{url}]({url})
'''

@click.command()
@click.option('--title',  help='記事のタイトル（日本語）')
@click.option('--category', default='その他', help='記事のカテゴリー(ボランティア、被災地、被災者向け、お役立ち、その他')
@click.option('--url', default='', help='情報元のURL')
@click.option('--excerpt', default='', help='記事の説明短文（一覧用）')
@click.argument('file')
def gen_news(title, category, excerpt, url, file):
    
    date = dt.now().strftime('%Y-%m-%d')
    updated = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    date_suffix = dt.now().strftime("%m%d")
    filename = "_posts/{}-{}-{}.md".format(date, file, date_suffix)

    click.echo(filename)
    with open(filename, 'w') as f:
        contents = template.format(
            title=title,
            category=category,
            excerpt=excerpt,
            date=updated + ' +0900',
            url=url)
        f.write(contents)

if __name__ == '__main__':
    gen_news() 