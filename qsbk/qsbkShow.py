#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
1.爬取糗事百科的所有热门评论
2.根据用户html页面请求
3.在html页面输出糗事百科的热门内容前几名

"""

from qsbkII import qsbk
import tornado.web
import tornado.ioloop

#定义空列表，保存数据库查询的结果
InputList=[]

#定义处理客户端请求的方法
class Runserver(tornado.web.RequestHandler):
    def get(self):
        self.render("qsbk.html",INP=InputList)

    def post(self, *args, **kwargs):
        oQsbk = qsbk()
        oQsbk.getALL()
        num=int(self.get_argument("num"))
        # print(num)
        InputList=oQsbk.getTopHot(num)

        self.render("qsbk.html",INP=InputList)


settings={
    "template_path":"template",
    "static_path":"static",
}

application=tornado.web.Application([
       (r"/index",Runserver),
      ],**settings)

if __name__ == '__main__':
    application.listen(8090)
    tornado.ioloop.IOLoop.instance().start()


