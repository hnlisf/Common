#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pymysql
InfoList=[]

def getTopComment(Num=5):
    # 每页内容写入一次数据库
    conn = pymysql.connect(host="localhost", port=3306, user="root", passwd="123456", db="python1702",
                           charset="utf8")
    cursor = conn.cursor()

    sqlStr = "SELECT content FROM qsbk ORDER BY vatenum DESC LIMIT %d"%Num
    try:
        effectRow = cursor.execute(sqlStr)
        if effectRow > 0:
            resultList = cursor.fetchall()

            print("热门前五的内容如下：")
            for i in range(len(resultList)):
                print("热门排名第%d:" % (i + 1), resultList[i][0])
                InfoList.append("热门排名第%d:" % (i + 1)+resultList[i][0])

            return InfoList
    except:
        print("查询数据库失败.........")

    cursor.close()
    conn.close()