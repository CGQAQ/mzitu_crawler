from dataclasses import dataclass

from bs4 import BeautifulSoup
import requests as rq
from os import system
import platform
import time
import os
import shutil

@dataclass
class Item:
    des: str
    url: str

@dataclass
class Img:
    des: str
    url: str
    ref: str

basicURL = 'https://www.mzitu.com/'
sortBy = [
    ''              # newest
    , 'hot/'        # hotest
    , 'best/'       # best
    , 'zhuanti/'    # collections
    , 'xinggan/'    # sexy
    , 'japan/'      # Japan
    , 'taiwan/'     # Taiwan
    , 'mm/'         # Innocent
]
    

def page_fun(n: int): 
    if n > 1:
        return f'page/{n}/'
    else:
        return ''

def select_type():
    global page, total_page
    page = 1
    t = None
    while t is None or int(t) >= len(sortBy) and int(t) <= 0:
        t = input('1.Newest\n2.Hot\n3.Best\n4.Zhuanti\n5.Sexy\n6.Japan\n7.Taiwan\n8.Innocent\nSelect type you want: ')
    global chooseType
    chooseType = False
    return int(t) - 1

def select_page():
    global page, chooseType
    n = input(f'current: {page}\t\ttotal_page: {total_page}\n- previous page\t\t+ next page\n 0: reselect type\nnumber start with letter d to download(d1 download second one):')
    if n == '-' and page > 1:
        page -= 1
    elif n == '+' and True:
        page += 1
    elif n == '0':
        chooseType = True
    elif n.isdigit() and int(n) > 0 and int(n) <= total_page:
        page = int(n)
    elif not n.isdigit() and str.startswith(n, 'd'):
        n = int(n[1:])
        download(collections[n].des, collections[n].url)

def download(name: str, url: str):
    # print(f'download: {url}')

    path_ = f'./{name}'
    if not os.path.exists(path_) or not os.path.isdir(path_):
        os.mkdir(path_)
    
    url_ = url
    print('Collecting info we need...')
    imgs = []
    while True:
        dr = rq.get(url_).text
        bs = BeautifulSoup(dr, 'html.parser')
        img = bs.select_one('img')
        imgs.append(Img(bs.select_one('.main-title').text, img['src'], url_))
        
        next = bs.select_one('div.pagenavi>:last-child')
        if next.select_one('span').text == '下一页»':
            url_ = next['href']
        else:
            break
        clear()
        print(f"Collecting: {bs.select('div.pagenavi>span:not(.dots)')[0].text} collected, {bs.select_one('div.pagenavi>:nth-last-child(2)').text} total")

    print('Download begin...')
    for i, img in enumerate(imgs):
        r = rq.get(img.url, stream=True, headers = {'Referer': img.ref})
        if r.status_code == 200: 
            with open(f"{path_}/{img.des}.{img.url.split('.')[-1]}", 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        clear()
        print(f"Downloading: {i} completed, {len(imgs)} total.")
        
    print('download completed.')
    time.sleep(1)
    pass

def clear():
    if platform is 'Windows':
        system('cls')
    else:
        system('clear')

chooseType = True
page = 1
total_page = None
collections = []

def main():
    global page, total_page, collections

    
    t = None
    while True:
        # start to requests
        collections = []
        if chooseType:
            t = select_type()
        mainpage_response = rq.get(basicURL + sortBy[t] + page_fun(page))
        bs_obj = BeautifulSoup(mainpage_response.text, 'html.parser')
        total_page = int(bs_obj.select_one('a.page-numbers:nth-last-child(2)').text)
        
        for li in bs_obj.select('ul#pins>li'):
            a = li.select_one('span>a')
            collections.append(Item(a.text, a['href']))
        
        for i, item in enumerate(collections):
            print(f'{str(i)}. {item.des}')
        select_page()
        
        clear()
        
    pass

if __name__ == '__main__':
    main()