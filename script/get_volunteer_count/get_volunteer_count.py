import urllib.request

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import pandas as pd

from time import sleep

FILENAME = 'data.csv'

def display():
    df = pd.read_csv('./'+ FILENAME, sep=',')
    print(df.head())


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select("#tablepress-7")
    
    ths = table[0].find_all("th")
    with open('./' + FILENAME, mode='w') as f:
        head = ','.join([t.text for t in ths])
        f.write(head)
        f.write('\n')

        trs = table[0].tbody.find_all("tr")
        for tr in trs:
            row = ','.join([td.text for td in tr.find_all("td")])
            if row.split(',')[0] != '':
                f.write(row)
                f.write('\n')
    display()


def main():
    url = 'https://ehimesvc.jp/?p=70'

    options = Options()
    options.set_headless(True)
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    sleep(1)

    select = Select(driver.find_element_by_name('tablepress-7_length'))
    select.select_by_index(2)
    sleep(1)

    html = driver.page_source.encode('utf-8')
    parse(html)


if __name__ == '__main__':
    main()