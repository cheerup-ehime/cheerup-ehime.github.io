#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime as dt

font = {'family': 'IPAexGothic'}
matplotlib.rc('font', **font)
import os
from PIL import Image

WEEKLY_GRAPH='./assets/images/volunteer_count_week.png'
DAILY_GRAPH='./assets/images/volunteer_count.png'
IMAGE_BASE_PATH = './assets/images/volunteer_headcount/'
IMAGE_NAME='{}_volunteer_headcount_diff_{}.png'
RECENT_HEADCOUNT_NAME='{}_volunteer_headcount_diff_recent.png'
VOLUNTEER_NEEDED='./_data/volunteer_needed.tsv'
GRAPH_SIZE=(12,12)

def save_as_jpeg(path):
    path_jpg = path.replace('png', 'jpg')
    Image.open(path).convert('RGB').save(path_jpg,'JPEG')

def load_data_from_site():
    url = 'https://ehimesvc.jp/?p=70'
    dfs = pd.read_html(url, index_col=0, na_values=['活動中止', '終了', '休止','－'])
    df = dfs[0]
    df.dropna(how='all', inplace=True)
    df.drop('合計', inplace=True)
    return df.rename(columns={'日付': 'Date'})

def load_volunteer_needed():
    df = pd.read_table(VOLUNTEER_NEEDED)
    return df[['Date', '宇和島市','大洲市','西予市']]

def now():
    return dt.datetime.now()
    # return (dt.datetime.now() - dt.timedelta(1)) #一日前で設定したい場合
    
def get_today(format):
    return dt.datetime.now().strftime(format)
    # return (dt.datetime.now() - dt.timedelta(1)).strftime(format) #一日前で設定したい場合

def df_with_date_index(df):
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    return df.set_index('Date').fillna(0).replace('',0).applymap(int)

# ボランティア数の必要数と実績グラフ出力
def gen_volunteer_needs_actual_graph(location, df1, df2):
    df = pd.DataFrame([df1[location], df2[location]]).T
    df.columns=['実績数','募集数']
    df.index.name='日付'
    df = df.sort_index()
    df.fillna(0, inplace=True)
    ax = df['2018-07-17':].plot(kind='area', 
                               figsize=GRAPH_SIZE,
                               alpha=0.4, 
                               stacked=False, 
                               fontsize=18,
                               title="{}災害VCボランティア募集数・実績数".format(location))
    fig = ax.get_figure()
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    today = get_today("%Y%m%d")

    fig.savefig(IMAGE_BASE_PATH + IMAGE_NAME.format(location, today))
    fig.savefig(IMAGE_BASE_PATH + RECENT_HEADCOUNT_NAME.format(location))
    save_as_jpeg(IMAGE_BASE_PATH +  IMAGE_NAME.format(location, today))
    return df

def gen_headcount_graph(df, df_needed):
    df_actual = df.iloc[:, [0,1,2,3]]
    df_needed = df_with_date_index(df_needed.iloc[:, [0,1,2,3]])

    gen_volunteer_needs_actual_graph('宇和島市', df_actual, df_needed)
    gen_volunteer_needs_actual_graph('大洲市', df_actual, df_needed)
    gen_volunteer_needs_actual_graph('西予市', df_actual, df_needed)


# ## ８日以内のデータのみフィルタする
def filter_within_week(df):
    return df.tail(8)
    # d_range = pd.date_range(end=get_today('%Y/%m/%d'), periods=8)
    # return df.loc[d_range]

# 前日比、前週比を出す。
def diff_another_day(df, before_day):
    df_top3 = df[['宇和島市','大洲市','西予市']]
    df_top3.fillna(0, inplace=True)
    df_top3.replace('', 0, inplace=True)
    df_top3 = df_top3.applymap(float)

    # before_day = now() - dt.timedelta(before_day)
    df_today = df_top3.iloc[-1]
    df_before = df_top3.iloc[(before_day + 1) * -1]
    # df_before = df_top3.loc[before_day.strftime('%Y-%m-%d')]
    return df_today - df_before

# 日次グラフ生成
def gen_day_graph(df):
    df2 = df.replace('', 0).fillna(0.0)
    df2.index.names = ['Date']
    df2 = filter_within_week(df2)
    print(df2)

    df2.index = df2.index.strftime("%m/%d")
    df2 = df2.applymap(float)
    ax = df2.plot(
                    kind='bar',
                    figsize=GRAPH_SIZE, 
                    alpha=0.5,
                    title="愛媛県ボランティア数動向（一週間）", 
                    subplots=False, 
                    stacked=True,
                    fontsize=20)

    plt.xlabel("日付", fontsize="20")
    plt.ylabel("人数", fontsize="20")
    plt.legend(fontsize="20")
    fig = ax.get_figure()
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
    # plt.show() 
    fig.savefig(DAILY_GRAPH)
    save_as_jpeg(DAILY_GRAPH)
    return df2

# 週次グラフ生成
def gen_week_graph(df):
    df2 = df.replace('', 0).fillna(0.0)
    df2.index.names = ['Date']

    # df2.index = df2.index.strftime("%m/%d")
    df2 = df2.applymap(float)
    df_w = df2.resample('W').sum()
    df_w.index = df_w.index.strftime("%m/%d週")
    ax = df_w.T.plot(kind='bar',
                        figsize=GRAPH_SIZE, 
                        alpha=0.5,
                        title="愛媛県ボランティア数動向（7月週別）", 
                        subplots=False, 
                        stacked=False,
                        fontsize=16)          
    plt.xlabel("自治体", fontsize="16")
    plt.ylabel("人数", fontsize="16")
    plt.legend(fontsize="16")
    fig = ax.get_figure()
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
    plt.legend(df_w.index, fontsize=18)
    fig.savefig(WEEKLY_GRAPH)
    save_as_jpeg(WEEKLY_GRAPH)
    return df_w

# Markdown Table生成
def gen_md_table(df):
    from tabulate import tabulate
    df.index.name = '日付'
    df = df.dropna()
    table = tabulate(df, tablefmt="pipe", headers="keys", showindex=True)
    return table

def choose_icon(num):
    if num == 0:
        return ':arrow_right:'
    elif num > 0:
        return ':arrow_upper_right:'
    else:
        return ':arrow_lower_right:'

def gen_row(df, area):
    row_tmpl = "{area} | {day_icon}{day_num} | {week_icon}{week_num}"
    df_yesterday = diff_another_day(df, 1)
    df_lastweek = diff_another_day(df, 7)
    return row_tmpl.format(
                area = area,
                day_icon = choose_icon(df_yesterday[area]),
                day_num = df_yesterday[area],
                week_icon = choose_icon(df_lastweek[area]),
                week_num = df_lastweek[area]
                )


def gen_diff_table(df):
    header = '''エリア | 前日比 | 前週同日比
---------|----------|---------'''
    table = [header]

    for area in ['宇和島市','大洲市','西予市']:
        table.append(gen_row(df, area))

    return "\n".join(table)

def write_article(table_diff, table_d, table_w):
    with open('./script/generate_volunteer_count/template.md') as f:
        template = f.read()
        
        ymd = now().strftime('%Y%m%d')
        month_day = now().strftime('%-m/%-d')
        timestamp = now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = template.format(
                        dateYMD=ymd,
                        month_day=month_day, 
                        timestamp=timestamp, 
                        table_diff=table_diff,
                        table_d=table_d, 
                        table_w=table_w)
        
        
    with open('./_pages/volunteer_aggregation.md', 'w') as f:
        f.write(report)

def write_post():
    with open('./script/generate_volunteer_count/post_template.md') as f:
        template = f.read()

        day = now().strftime('%m%d')
        month_day = now().strftime('%-m/%-d')
        ymd = now().strftime("%Y-%m-%d")
        timestamp = now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = template.format(
                        month_day=month_day, 
                        timestamp=timestamp)

    with open('./_posts/{}-volunteer-aggregation-{}.md'.format(ymd, day), 'w') as f:
        f.write(report)
    


if __name__ == '__main__':
    df_needed = load_volunteer_needed()
    df = load_data_from_site()
    df = df.rename(index=lambda s: dt.datetime.strptime(s, '%m月%d日').replace(year=2018))
    gen_headcount_graph(df, df_needed)
    df_d = gen_day_graph(df)
    df_w = gen_week_graph(df)
    table_diff = gen_diff_table(df)
    table_d = gen_md_table(df_d)
    table_w = gen_md_table(df_w)
    write_article(table_diff, table_d, table_w)
    write_post()

