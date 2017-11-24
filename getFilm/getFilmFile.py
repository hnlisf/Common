#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
爬取电影之家上所有电影的下载连接，电影名和imdb评分
将数据存入数据库
"""
import threading

import requests
import time
from bs4 import BeautifulSoup
import pymysql
import re



startUrl="http://www.dytt8.net/html/gndy/dyzz/index.html"



#找出电影之家所有页面的链接地址
def getPageUrllist(startUrl):
    mpattrn="<option value='(.+)'(\sselected)?>\d+</option>"
    reoption=re.compile(mpattrn)
    baseUrl="http://www.dytt8.net/html/gndy/dyzz/"
    pageUrlList=[]

    resp=requests.get(startUrl)
    html=resp.text
    optionlist=reoption.findall(html)

    #将匹配的option与baseUrl做拼接
    for option in optionlist:
        pageUrlList.append(baseUrl+option[0])
    # print(pageUrlList)
    return pageUrlList

#获得当前页面中所有电影的电影名称，IMDB，下载链接
def getPageFilmInfo(pageUrl,sem):
    with sem:

        mpattion="◎IMDb评分 (\d.\d)/"
        reIMDB=re.compile(mpattion)


        print(pageUrl)
        #将请求编码设置为gbk，解决中文乱码问题
        resp=requests.get(pageUrl)
        resp.encoding="gbk"

        soup=BeautifulSoup(resp.text,"html.parser")

        tag_table_list=soup.find_all("table",class_="tbspan")
        # print(len(tag_table_list),tag_table_list)

        for tag_table in tag_table_list:
            tag_a=tag_table.find_all("a")[0]
            #找到电影名称
            filmName=tag_a.text
            urloption=tag_a["href"]
            filmPageUrl="http://www.dytt8.net"+urloption
            print(filmPageUrl)

            #获得IMDB评分，若无评分，则设置为”-1“
            try:
                tag_td=tag_table.find_all(style="padding-left:3px")[2]
                IMDB=reIMDB.search(tag_td.text).group(1)
            except AttributeError:
                IMDB="-1"


            #获得电影文件下载链接
            ftpUrl=getFilmDownUrl(filmPageUrl)

            print(filmName,IMDB,ftpUrl)
            #写入数据库
            writeDataBase(filmName,IMDB,ftpUrl)
            time.sleep(1)
            print("全部信息已写入数据库")

#获取ftp下载链接
def getFilmDownUrl(url):
    mpattrn="(ftp:\S+)\""
    html=requests.get(url).content.decode("gbk")
    ftpUrl=re.findall(mpattrn,html)[0]
    return ftpUrl


#写入数据库
def writeDataBase(filmName,IMDB,ftpUrl):
    conn=pymysql.connect(host="127.0.0.1",port=3306,user="root",passwd="123456",db="film",charset="utf8")
    cursor=conn.cursor()

    sqlstr="insert into filmDownUrl (filmname,IMDB,ftpurl) VALUES ('%s',%f,'%s')"%(filmName,eval(IMDB),ftpUrl)

    effectRow=cursor.execute(sqlstr)

    if effectRow:
        print(filmName,"写入数据库成功")
    conn.commit()
    cursor.close()
    conn.close()





if __name__ == '__main__':
    #获取所有电影天堂页面链接
    pageUrllist=getPageUrllist(startUrl)
    #设置线程并发为10
    sem=threading.Semaphore(10)
    tlist=[]

    print(pageUrllist)
    #开启线程池进行爬取
    for pageUrl in pageUrllist:
        t=threading.Thread(target=getPageFilmInfo,args=(pageUrl,sem))
        t.start()
        tlist.append(t)

    #保持子线程运行时，主线程阻塞
    for t in tlist:
        t.join()

