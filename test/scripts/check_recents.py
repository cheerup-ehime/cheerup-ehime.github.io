from urllib.parse import urlparse,urljoin
from bs4 import BeautifulSoup
import requests 
import pickle

def formatPost(event):
    #140文字制限にひっかからないようにイベント名スライス
    return "{0}\n{1}\n{2}".format(event[0],event[1][:140-len(event[0])-len(event[2])],event[2])

def getEvents():
    #晒すとまずそうなので
    url_list [
        'http://seiyo-syakyo.jp/',
        'http://www.imabari-shakyo.jp/',
        'http://www.uwajima-shakyo.or.jp/',
        'http://www.city.ozu.ehime.jp/',
    root = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
    #証明書エラーを無視
    r = requests.get(url, verify=False)
    soap = BeautifulSoup(r.text,"lxml")

    #Only the following pseudo-classes are implemented: nth-of-type.
    #chromeの開発ツール->copy selectorでcssセレクタをコピってきて実行するとエラーになるので一部要変更
    #こんな感じ li:nth-child(1) -> li:nth-of-type(1)
    #必要な要素だけタプル型(dictとか可変の型はNGっぽい)で抽出して集合に突っ込む
    set_evnets = {(div.select("header > ul > li:nth-of-type(1) > span.c-eventSummary-datetime > time")[0].text,
                   div.select("header > a > h2 > span")[0].text,
                   urljoin(root,div.select("div.c-eventSummary-image.js-eventSummary-image > a:nth-of-type(1)")[0].get("href"))) 
                   for div in soap.select("#eventlist > div > article")}

    #前回取得分復元
    try:
        with open('events.pickle', 'rb') as f:  
            set_evnets_old = pickle.load(f)
    except:
        set_evnets_old = set()

    #今回取得分で上書き保存
    with open('events.pickle', 'wb') as f:
        pickle.dump(set_evnets, f)

    #今回分-前回分のリストをツイートできるように整形して返す
    return list(map(formatPost,set_evnets - set_evnets_old))

if __name__ == "__main__":
    for event in getEvents():
        #tweetしたかったらこんな感じで実装すればおk
        #post(event)