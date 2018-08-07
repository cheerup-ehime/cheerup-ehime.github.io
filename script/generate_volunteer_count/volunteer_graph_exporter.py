
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
# import gspread as gs
from PIL import Image

#from oauth2client.service_account import ServiceAccountCredentials

WEEKLY_GRAPH='./assets/images/volunteer_count_week.png'
DAILY_GRAPH='./assets/images/volunteer_count.png'

# In[33]:

def load_data_from_site():
    url = 'https://ehimesvc.jp/?p=70'
    dfs = pd.read_html(url, index_col=0, na_values=['活動中止', '終了', '休止'])
    df = dfs[0]
    df.dropna(how='all', inplace=True)
    df.drop('合計', inplace=True)
    return df.rename(columns={'日付': 'Date'})


# def create_google_client(path):
#     scope = ['https://spreadsheets.google.com/feeds']
#     path = os.path.expanduser(path)
#     credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
#     client = gs.authorize(credentials)
#     return client

def save_as_jpeg(path):
    path_jpg = path.replace('png', 'jpg')
    Image.open(path).convert('RGB').save(path_jpg,'JPEG')

# In[34]:

# def load_data_from_gspread():

#     path = '/Users/kkd/.credential/Dataprep-770b3144dc97.json'
#     doc_url = 'https://docs.google.com/spreadsheets/d/1h-GFHoNa55P96wu_HNbPk899eN4HZcnu1T9q4eag8Uc/edit?usp=sharing'

#     client = create_google_client(path)
#     gfile = client.open_by_url(doc_url)
#     worksheet = gfile.worksheet('volunteer')
#     records = worksheet.get_all_values()
#     cols_name = records[0]
#     data = records[1:]
#     df = pd.DataFrame(data=data, columns=cols_name)
#     return df[['Date','宇和島市','大洲市','西予市','今治市','松山市']]

# ## ８日以内のデータのみフィルタする
def filter_within_week(df):
    # today = (dt.datetime.now() - dt.timedelta(1)).strftime('%Y/%m/%d')
    today = dt.datetime.now().strftime('%Y/%m/%d')
    d_range =  pd.date_range(end=today, periods=8)
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

# ## Excelデータを元にグラフを出力
# df = pd.read_excel('assets/data/ehime_volunteer.xlsx')


def generate_graph_within_week(df):
    df.replace('', 0, inplace=True)
    df.fillna(0, inplace=True)

    df2 = df
    df2.index.names = ['Date']
    print(df2.head())

    df2 = filter_within_week(df2)
    print(df2)
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

def generage_week_graph(df):
    df.replace('', 0, inplace=True)
    df.fillna(0, inplace=True)

    df2 = df
    df2.index.names = ['Date']

    # df2.index = df2.index.strftime("%m/%d")
    df2 = df2.applymap(float)
    df_w = df2.resample('W').sum()
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
    plt.legend(df_w.index.strftime("%m/%d週"),
                    fontsize=18)
    fig.savefig(WEEKLY_GRAPH)
    save_as_jpeg(WEEKLY_GRAPH)
    return df_w

# In[37]:

def generate_table(df):
    from tabulate import tabulate

    # df_table = df.set_index('Date')
    # df_table.index = df_table.index.strftime('%m/%d')
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

# In[38]:

def write_article(table_diff, table_d, table_w):
    from datetime import datetime as dt
    with open('./script/generate_volunteer_count/template.md') as f:
        template = f.read()
        
        month_day = dt.now().strftime('%m/%d')
        timestamp = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = template.format(month_day=month_day, 
                        timestamp=timestamp, 
                        table_diff=table_diff,
                        table_d=table_d, 
                        table_w=table_w)
        
        
    with open('./_pages/volunteer_aggregation.md', 'w') as f:
        f.write(report)
    

if __name__ == '__main__':
    # df = load_data_from_gspread()
    df = load_data_from_site()
    df = df.rename(index=lambda s: dt.datetime.strptime(s, '%m月%d日').replace(year=2018))
    df_d = generate_graph_within_week(df)
    df_w = generage_week_graph(df)
    table_diff = generate_diff_table(df)
    table_d = generate_table(df_d)
    table_w = generate_table(df_w)
    write_article(table_diff, table_d, table_w)

