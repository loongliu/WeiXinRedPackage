# coding=utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import options, define

from motor import MotorClient
from orm import MongoOrm

from handler import handlers

define("port", default=18000, help="本地监听端口", type=int)
define("DEBUG", default=True, help="是否开启debug模式", type=bool)
define("TEST",default=False,help="测试服务器，支持跨域访问,推送测试模式",type=bool)
define("mongo_db", default="redpackage", help="mongo数据", type=str)
tornado.options.parse_command_line()

mongo_client = MotorClient('localhost:27017')

application = tornado.web.Application(
    handlers=handlers,
    db = MongoOrm(mongo_client[options.mongo_db]),
    TEST = options.TEST,
    debug = options.DEBUG,
    compiled_template_cache = True,
    static_hash_cache = True,
    autoreload = True
)
application.listen(options.port)
ioloop = tornado.ioloop.IOLoop.current()

ioloop.start()
