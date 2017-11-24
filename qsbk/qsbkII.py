#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
采用类方法
1.爬取糗事百科的所有热门评论、发布者，点赞数
2.输出糗事百科的热门内容前五名

"""

import requests
from bs4 import BeautifulSoup
import re
import pymysql
from threading import Thread

InfoList=[]
class qsbk:
    def __init__(self):
        self.baseUrl="https://www.qiushibaike.com/hot/page/"
        self.headers={
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.9 Safari/537.36"
                     }
        self.pageNum=0
        # 清空数据库
        self.clearDB()

    # 清空数据库
    def clearDB(self):
        conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="123456", db="python1702",
                               charset="utf8")
        cursor = conn.cursor()
        # 先清空数据库
        try:
            cursor.execute("delete from qsbk WHERE nid>0")
            print("已清空数据库")

        except:
            print("清空数据库失败")

        conn.commit()
        cursor.close()
        conn.close()



    # 获取热门评论的页数
    def getPageNum(self):
        rep = requests.get(self.baseUrl, headers=self.headers, timeout=5)
        soup = BeautifulSoup(rep.text, "html.parser")
        ulTag = soup.find("ul", class_="pagination")

        # 找到ul倒数第二个li标签的文本内容
        pageNum = int(ulTag.find_all("li")[-2].find("span").text.strip())

        return pageNum

    # 获得页面的热门评论
    def getPageInfo(self,url):
        rep = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(rep.text, "html.parser")
        contentList = soup.find_all(id=re.compile("qiushi_tag_\d+"))
        # 保存当前所有热门评论、发布者，点赞数信息的列表
        infoList = []

        # print(len( contentList))
        for item in contentList:
            userName = item.find("h2").text.strip()
            contentText = item.find("span").text.strip()
            # 当文本内容不为空时
            if contentText != "":
                voteNum = item.find("span", class_="stats-vote").find("i").text
                commentNum = item.find("span", class_="stats-comments").find("i").text
                infoList.append([userName, contentText, voteNum, commentNum])


        # 每页内容写入一次数据库
        conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="123456", db="python1702",
                               charset="utf8")
        cursor = conn.cursor()


        # 通过循环来写入数据库
        for info in infoList:
            self.wirteDB(cursor, info[0], info[1], info[2], info[3])

        conn.commit()
        cursor.close()
        conn.close()

        print("%s,网页内容已写入数据库" % url)

    #写入数据库
    def wirteDB(self,cursor,userName,contentText,voteNum,commentNum):



        sqlStr = "INSERT INTO qsbk(usename,content,vatenum,commentnum) VALUES('%s','%s',%d,%d)" % (
        userName, contentText, int(voteNum), int(commentNum))
        # print(sqlStr)

        try:
            cursor.execute(sqlStr)
            print("用户%s发布内容已写入数据库" % userName)
        except:
            print("用户%s发布内容写入数据库失败" % userName)

    # 多线程执行多页
    def getALL(self):

        pageNum=self.getPageNum()
        # 线程列表
        tlist = []

        # 开启子线程
        for i in range(pageNum):
            url = self.baseUrl + str(i + 1) + "/"
            t = Thread(target=self.getPageInfo, args=(url,))
            tlist.append(t)
            t.start()

        # 保持所有子线程执行
        for t in tlist:
            t.join()

        print("所有糗事百科热门内容已写入数据库.....")

    #     获得前五的热门评论
    def getTopHot(self,Num=5):
        conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="123456", db="python1702",
                               charset="utf8")
        cursor = conn.cursor()

        sqlStr = "SELECT content FROM qsbk ORDER BY vatenum DESC LIMIT %d" % Num
        try:
            effectRow = cursor.execute(sqlStr)
            if effectRow > 0:
                resultList = cursor.fetchall()

                print("热门前五的内容如下：")
                for i in range(len(resultList)):
                    print("热门排名第%d:" % (i + 1), resultList[i][0])
                    InfoList.append("热门排名第%d:" % (i + 1) + resultList[i][0])

                return InfoList
        except:
            print("查询数据库失败.........")

        cursor.close()
        conn.close()

if __name__ == '__main__':
    oQsbk=qsbk()
    oQsbk.getALL()
    oQsbk.getTopHot()