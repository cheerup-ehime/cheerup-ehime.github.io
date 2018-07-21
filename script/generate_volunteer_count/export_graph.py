
# coding: utf-8

# In[32]:


import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime as dt
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
get_ipython().run_line_magic('matplotlib', 'inline')
font = {'family': 'IPAexGothic'}
matplotlib.rc('font', **font)
import os
import gspread as gs

from oauth2client.service_account import ServiceAccountCredentials


# In[33]:


def create_google_client(path):
    scope = ['https://spreadsheets.google.com/feeds']
    path = os.path.expanduser(path)
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
    client = gs.authorize(credentials)
    return client


# In[34]:



path = '/Users/kkd/.credential/Dataprep-770b3144dc97.json'
doc_url = 'https://docs.google.com/spreadsheets/d/1h-GFHoNa55P96wu_HNbPk899eN4HZcnu1T9q4eag8Uc/edit?usp=sharing'

client = create_google_client(path)
gfile = client.open_by_url(doc_url)
worksheet = gfile.worksheet('volunteer')
records = worksheet.get_all_values()
cols_name = records[0]
data = records[1:]
df = pd.DataFrame(data=data, columns=cols_name)
df


# ## Excelデータを元にグラフを出力
# 
# Excelファイルは[Google Drive](https://docs.google.com/spreadsheets/d/1h-GFHoNa55P96wu_HNbPk899eN4HZcnu1T9q4eag8Uc/edit#gid=0)からダウンロードした後で読み込んでいる。
# (直接読み込むようにしたい。。。）

# In[36]:


# df = pd.read_excel('assets/data/ehime_volunteer.xlsx')
df.replace('', 0, inplace=True)
df.fillna(0, inplace=True)

df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
df2 = df.set_index('Date')
df2.index.names = ['Date']

df2.index = df2.index.strftime("%m/%d")
df2 = df2.applymap(int)
df2.describe()

ax = df2.plot(
                        kind='bar', 
                        figsize=(16,10), 
                        alpha=0.5,
                        title="愛媛県ボランティア数（7月）", 
                        subplots=False, 
                        stacked=True,
                        fontsize=20)

plt.xlabel("月日", fontsize="20")
plt.ylabel("人数", fontsize="20")
plt.legend(fontsize="20")
fig = ax.get_figure()
for tick in ax.get_xticklabels():
    tick.set_rotation(45)
plt.show() 
fig.savefig('../../assets/images/volunteer_count.png')




# In[37]:


get_ipython().system('pip install tabulate')
from tabulate import tabulate

df_table = df.set_index('Date')
df_table.index = df_table.index.strftime('%m/%d')
df_table.index.name = '日付'

table = tabulate(df_table, tablefmt="pipe", headers="keys", showindex=True)


# In[38]:


from datetime import datetime as dt
with open('template.md') as f:
    template = f.read()
    
    month_day = dt.now().strftime('%m/%d')
    timestamp = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = template.format(month_day=month_day, timestamp=timestamp, table=table)
    
    
with open('../../_pages/volunteer_aggregation.md', 'w') as f:
    f.write(report)
    

        

