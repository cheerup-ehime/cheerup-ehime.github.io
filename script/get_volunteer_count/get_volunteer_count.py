import pandas as pd

def main():
    url = 'https://ehimesvc.jp/?p=70'

    dfs = pd.read_html(url, index_col=0, na_values=['活動中止', '終了', '休止'])
    df = dfs[0]
    df.dropna(how='all', inplace=True)
    df.drop('合計', inplace=True)
    print(df.head())

if __name__ == '__main__':
    main()