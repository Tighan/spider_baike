#coding:utf-8
'''
Created on 2016.1.9
@author: Tighan
'''
import urllib.request
from bs4 import BeautifulSoup
import re
import sqlite3
import time

class UrlManger(object):
    
    def __init__(self):
        self.new_urls = set()
        self.old_urls = set()
    def add_url(self,url):
        if url is None:
            return
        if url not in self.new_urls and url not in self.old_urls:
            self.new_urls.add(url)
    
    def has_newurl(self):
        return len(self.new_urls) != 0

    def get_new_url(self):
        new_url = self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url
    def add_new_urls(self,urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_url(url)
  

class DownLoader(object):
    
    def downloader(self,url):
        source = urllib.request.urlopen(url)
        html_source = source.read()
        return html_source
    

class Parser(object):
    
    
    def html_parser_url(self,source):
        urls=set()
        soup=BeautifulSoup(source,'html.parser')
        links=soup.find_all("a",href=re.compile(r"/view/\d+\.htm"))
        for link in links:
            url = 'http://baike.baidu.com'+link['href']
            urls.add(url)
        return urls
    def html_parser_data(self,new_url,source):
        soup = BeautifulSoup(source,'html.parser')
        summary = soup.find("div",class_="lemma-summary").text
        title = soup.find("h1").text
        data = (title,summary,new_url)
        return data

    
    def html_parser(self,new_url,page):
        urls = self.html_parser_url(page)
        data = self.html_parser_data(new_url,page)
        return urls,data
    
    
class DataBase(object):
    def __init__(self):
        self.database = sqlite3.connect('baidubaike')
        self.cu = self.database.cursor()
        try:
            self.cu.execute("create table baike (id integer primary key autoincrement,title,summary,url)")
        except:
            pass
        
    #create table user(_id integer primary key autoincrement, username char(20), password char(20))   
    #data = (title,summary,new_url)
    def add_data(self,data):
        self.cu.execute("insert into  baike values (null,?,?,?)", data)
        self.database.commit()    

class SpiderMain(object):
    def __init__(self):
        self.urls = UrlManger()
        self.down = DownLoader()
        self.parser = Parser()  
        self.database = DataBase()
    def start(self,root_url):
        self.urls.add_url(root_url)
        while self.urls.has_newurl():
            timecount = 0
            try:
                new_url = self.urls.get_new_url()
                page = self.down.downloader(new_url)
                new_urls,data = self.parser.html_parser(new_url,page)
                self.urls.add_new_urls(new_urls)
                self.database.add_data(data)
                timecount += 1
                if timecount == 60:
                    time.sleep(30)
                    timecount = 0
            except:
                raise

if __name__=='__main__':
    root_url = 'http://baike.baidu.com/view/21087.htm'
    obj_spider = SpiderMain()
    obj_spider.start(root_url)
    