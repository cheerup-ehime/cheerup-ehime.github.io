
# coding: utf-8

# In[32]:


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
VOLUNTEER_NEEDED='./_data/volunteer_needed.tsv'

def save_as_jpeg(path):
    path_jpg = path.replace('png', 'jpg')
    Image.open(path).convert('RGB').save(path_jpg,'JPEG')

def load_data_from_site():
    url = 'https://ehimesvc.jp/?p=70'
    dfs = pd.read_html(url, index_col=0, na_values=['活動中止', '終了', '休止'])
    df = dfs[0]
    df.dropna(how='all', inplace=True)
    df.drop('合計', inplace=True)
    return df.rename(columns={'日付': 'Date'})

def load_volunteer_needed():
    df = pd.read_table(VOLUNTEER_NEEDED)
    print(df)
    return df[['Date', '宇和島市','大洲市','西予市']]

def get_today(format):
    return dt.datetime.now().strftime(format)
    # return (dt.datetime.now() - dt.timedelta(1)).strftime(format) #一日前で設定したい場合

def df_with_date_index(df):
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    return df.set_index('Date').fillna(0).replace('',0).applymap(int)

def generate_voluneer_needs_actual_graph(location, df1, df2):
    df = pd.DataFrame([df1[location], df2[location]]).T
    df.columns=['実績数','募集数']
    df.index.name='日付'
    df = df.sort_index()
    df.fillna(0, inplace=True)
    ax = df['2018-07-17':].plot(kind='area', 
                               figsize=(10,10),
                               alpha=0.4, 
                               stacked=False, 
                               fontsize=18,
                               title="{}災害VCボランティア募集数・実績数".format(location))
    fig = ax.get_figure()
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    today = get_today("%Y%m%d")

    fig.savefig(IMAGE_BASE_PATH + IMAGE_NAME.format(location, today))
    save_as_jpeg(IMAGE_BASE_PATH +  IMAGE_NAME.format(location, today))
    return df

def generate_ratio_of_volunteer_needs(df, df_needed):
    df_actual = df.iloc[:, [0,1,2,3]]
    df_needed = df_with_date_index(df_needed.iloc[:, [0,1,2,3]])

    generate_voluneer_needs_actual_graph('宇和島市', df_actual, df_needed)
    generate_voluneer_needs_actual_graph('大洲市', df_actual, df_needed)
    generate_voluneer_needs_actual_graph('西予市', df_actual, df_needed)


# ## ８日以内のデータのみフィルタする
def filter_within_week(df):
    d_range = pd.date_range(end=get_today('%Y/%m/%d'), periods=8)
    print(d_range)
    return df.loc[d_range]

# 前日比、前週比を出す。
def diff_another_day(df, before_day):
    df_top3 = df[['宇和島市','大洲市','西予市']]
    df_top3.fillna(0, inplace=True)
    df_top3.replace('', 0, inplace=True)
    df_top3 = df_top3.applymap(float)

    before_day = dt.datetime.now() - dt.timedelta(before_day)
     
    df_today = df_top3.iloc[-1]
    df_before = df_top3.loc[before_day.strftime('%Y-%m-%d')]
    return df_today - df_before

# 日次グラフ生成
def generate_graph_within_week(df):
    df.replace('', 0, inplace=True)
    df.fillna(0, inplace=True)

    df2 = df
    df2.index.names = ['Date']
    df2 = filter_within_week(df2)

    df2.index = df2.index.strftime("%m/%d")
    df2 = df2.applymap(float)
    ax = df2.plot(
                    kind='bar',
                    figsize=(8,8), 
                    alpha=0.5,
                    title="愛媛県ボランティア数動向（一週間）", 
                    subplots=False, 
                    stacked=True,
                    fontsize=16)

    plt.xlabel("日付", fontsize="16")
    plt.ylabel("人数", fontsize="16")
    plt.legend(fontsize="16")
    fig = ax.get_figure()
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
    # plt.show() 
    fig.savefig(DAILY_GRAPH)
    save_as_jpeg(DAILY_GRAPH)
    return df2

# 週次グラフ生成
def generage_week_graph(df):
    df.replace('', 0, inplace=True)
    df.fillna(0, inplace=True)

    df2 = df
    df2.index.names = ['Date']

    # df2.index = df2.index.strftime("%m/%d")
    df2 = df2.applymap(float)
    df_w = df2.resample('W').sum()
    df_w.index = df_w.index.strftime("%m/%d週")
    ax = df_w.T.plot(kind='bar',
                        # figsize=(16,10), 
                        figsize=(8,8), 
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
def generate_table(df):
    from tabulate import tabulate
    df.index.name = '日付'
    table = tabulate(df, tablefmt="pipe", headers="keys", showindex=True)
    return table

def choose_icon(num):
    if num == 0:
        return ':arrow_right:'
    elif num > 0:
        return ':arrow_upper_right:'
    else:
        return ':arrow_lower_right:'

def generate_diff_table(df):
    diff_table = '''エリア | 前日比 | 前週同日比
---------|----------|---------
 宇和島市 | {uwa_diff_yesterday_icon}{uwa_diff_yesterday_num} | {uwa_diff_lastweek_icon}{uwa_diff_lastweek_num}
 大洲市  | {ozu_diff_yesterday_icon}{ozu_diff_yesterday_num} | {ozu_diff_lastweek_icon}{ozu_diff_lastweek_num}
 西予市  | {seiyo_diff_yesterday_icon}{seiyo_diff_yesterday_num} | {seiyo_diff_lastweek_icon}{seiyo_diff_lastweek_num}
'''
    df_yesterday = diff_another_day(df, 1)
    df_lastweek = diff_another_day(df, 7)

    return diff_table.format(
        uwa_diff_yesterday_icon=choose_icon(df_yesterday['宇和島市']),
        uwa_diff_yesterday_num=df_yesterday['宇和島市'],
        ozu_diff_yesterday_icon=choose_icon(df_yesterday['大洲市']),
        ozu_diff_yesterday_num=df_yesterday['大洲市'],
        seiyo_diff_yesterday_icon=choose_icon(df_yesterday['西予市']),
        seiyo_diff_yesterday_num=df_yesterday['西予市'],
        uwa_diff_lastweek_icon=choose_icon(df_lastweek['宇和島市']),
        uwa_diff_lastweek_num=df_lastweek['宇和島市'],
        ozu_diff_lastweek_icon=choose_icon(df_lastweek['大洲市']),
        ozu_diff_lastweek_num=df_lastweek['大洲市'],
        seiyo_diff_lastweek_icon=choose_icon(df_lastweek['西予市']),
        seiyo_diff_lastweek_num=df_lastweek['西予市'])

def write_article(table_diff, table_d, table_w):
    from datetime import datetime as dt
    with open('./script/generate_volunteer_count/template.md') as f:
        template = f.read()
        
        ymd = dt.now().strftime('%Y%m%d')
        month_day = dt.now().strftime('%-m/%-d')
        timestamp = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = template.format(
                        dateYMD=ymd,
                        month_day=month_day, 
                        timestamp=timestamp, 
                        table_diff=table_diff,
                        table_d=table_d, 
                        table_w=table_w)
        
        
    with open('./_pages/volunteer_aggregation.md', 'w') as f:
        f.write(report)

if __name__ == '__main__':
    df_needed = load_volunteer_needed()
    df = load_data_from_site()
    df = df.rename(index=lambda s: dt.datetime.strptime(s, '%m月%d日').replace(year=2018))
    generate_ratio_of_volunteer_needs(df, df_needed)
    df_d = generate_graph_within_week(df)
    df_w = generage_week_graph(df)
    table_diff = generate_diff_table(df)
    table_d = generate_table(df_d)
    table_w = generate_table(df_w)
    write_article(table_diff, table_d, table_w)

