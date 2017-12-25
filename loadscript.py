#-*-coding: utf-8 -*-
import urllib.request
import json
from bs4 import BeautifulSoup
import os
import codecs
import csv
from pymongo import MongoClient
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler


url_dailynews = "https://www.dailynews.co.th/sports?page="
url_kaosod = "https://www.khaosod.co.th/sports/page/"
url_matichon = "https://www.matichon.co.th/category/economy/page/"

path_file = "/Users/jirayutk./Project/projectfile/newsfile/"

# ------------------------------------------------DailyNews-------------------------------------------
def get_dailynews_url(url_page):
    response = urllib.request.urlopen(url_page)
    html = response.read()

    soup = BeautifulSoup(html, "html.parser")
    post_data = []
    for x in soup.find_all("div", class_=('left')):
        for xx in x.find_all("article",class_=('content ')):
            try:
                link = xx.a.get('href')
                print(link)
                post_data.append(get_news(link))
            except:
                continue
    insert_mongo(post_data)
def get_news(url_text):
    body = ''
    title = ''
    subtitle = ''
    type = ''
    inNews = False

    response = urllib.request.urlopen(url_text)
    html = response.read()

    soup = BeautifulSoup(html,"html.parser")
    for list in soup.find_all("section",class_=('article-detail')):
        for result in list.find_all("div",class_=('entry textbox content-all')):
            body = result.get_text()
    body = body.replace("googletag.cmd.push(function() { googletag.display('div-gpt-ad-8668011-5'); });","")#.translate(str.maketrans('', '', string.whitespace))
    for tag in soup.find_all("ol",class_=('breadcrumb')):
        try:
            if "ข่าวเดลินิวส์" in str(tag.find_all("li")):
                isNews = True
                for tag2 in tag.find_all("li"):
                    type = tag2.get_text()
                    if "ข่าวเดลินิวส์" not in str(tag2) and "หน้าแรก" not in str(tag2):
                        type = tag2.get_text()
            else:
                isNews = False
                break
        except:
            continue
    type = type.strip()
    title = soup.find("h1",class_=('title')).get_text().strip()
    subtitle = soup.find("p", class_=('desc')).get_text().strip()
    tmp = soup.find("span", class_=('date')).get_text().strip()
    subtitle = str(subtitle).replace(tmp,"")
    if isNews:
        return add_json(type,title,subtitle,body)

def insert_mongo(data):
    # ----------MongoDB connect ------------
    client = MongoClient()
    client = MongoClient('mongodb://admin:admin@ds131237.mlab.com:31237/news_data')

    db = client['news_data']
    collection = db['news']

    result = db.news.insert_many(data)
    print(db.news.count())

def add_json(type,title,subtitle,body):
    data = {"type": str(type).strip(), "title": str(title).strip(), "subtitle": str(subtitle).strip(),
            "body": str(body).strip()}
    #json_data = json.dumps(data)
    #file = open(path_file+"dailynews/news_sports.txt",'a')
    #file.writelines(json_data+"\n")
    #file.close()
    ob_data = {"news":"dailynews",
                "type": str(type).strip(),
                "title": str(title).strip(),
                "subtitle": str(subtitle).strip(),
                "body": str(body).strip(),
                "date": datetime.datetime.utcnow()}
    return ob_data

def load_dailynews_tofile():
    typefile = "new_type.csv"
    with open(typefile, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            url_page = "https://www.dailynews.co.th/"+row['dailynews']+"?page=1"
            get_dailynews_url(url_page)
            #for i in range(1,2):
             #   print(url_page+str(i))
             #   get_dailynews_url(url_page+str(i))

#------------------------------------------------DailyNews-------------------------------------------

#------------------------------------------------Kaosod-------------------------------------------
def get_kaosod_url(url_text):
    response = urllib.request.urlopen(url_text)
    html = response.read()

    soup = BeautifulSoup(html, "html.parser")
    data = []
    for x in soup.find_all("div",class_=('ud_loop_inner')):
        for link in x.find_all("h3",class_=('entry-title td-module-title')):
            try:
                urllink = link.a.get('href')
                print(urllink)
                data.append(get_kaosod_news(urllink,"khaosod"))
            except:
                continue
    insert_mongo(data)
def get_kaosod_news(url_link,news):
    type = ""
    title = ""
    subtitle = ""
    body = ""

    response = urllib.request.urlopen(url_link)
    html = response.read()

    soup = BeautifulSoup(html, "html.parser")
    for x in soup.find_all("div",class_=('entry-crumbs')):
        for xx in x.find_all("a"):
            if "หน้าแรก" not in xx.get_text():
                type = xx.get_text()
    for x in soup.find_all("h1",class_=('entry-title')):
        title = x.get_text()
    for x in soup.find_all("p"):
        body = body+x.get_text()
    return write_file_kaosod(type, title,subtitle, body,news)
def write_file_kaosod(type,title,subtitle,body,news):
    #data = {"type": str(type).strip(), "title": str(title).strip(),"body": str(body).strip()}
    #json_data = json.dumps(data)
    #file = open("/Users/jirayutk/Project/Seniorproject/Deepcut/newsfile/news_economy.txt", 'a')
    #file.writelines(json_data + "\n")
    #file.close()
    ob_data = {"news": news,
               "type": str(type).strip(),
               "title": str(title).strip(),
               "subtitle": str(subtitle).strip(),
               "body": str(body).strip(),
               "date": datetime.datetime.utcnow()}
    return ob_data

def load_kaosod():
    #for i in range(1,20):
    #    print (str(i))
    #    get_kaosod_url(url_kaosod+str(i))
    typefile = "new_type.csv"
    with open(typefile, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row['khaosod'])
            url_page = "https://www.khaosod.co.th/"+ row['khaosod'] +"/page/1"
            get_kaosod_url(url_page)




 #------------------------------------------------Kaosod-------------------------------------------

#------------------------------------------------matichon----------------------------------------
def get_urls_matichon(url_page):
    response = urllib.request.urlopen(url_page)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")
    data = []
    for tag in soup.find_all("h3",class_=('entry-title td-module-title')):
        try:
            link = tag.a.get('href')
            print(link)
            data.append(get_kaosod_news(link,"matichon"))
        except:
            continue
    insert_mongo(data)
def load_matichon():
    #for i in range(210,400):
    #    print (str(i))
    #    get_urls_matichon(url_matichon+str(i))
    typefile = "new_type.csv"
    with open(typefile, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row['matichon'])
            url_page = "https://www.matichon.co.th/category/" + row['matichon'] + "/page/1"
            get_urls_matichon(url_page)

#------------------------------------------------matichon----------------------------------------



def main():
    try:
        load_kaosod()
        load_matichon()
        load_dailynews_tofile()
        print("Loading Script Success")
    except Exception as e:
        print(e)
if __name__ == '__main__':
    main()