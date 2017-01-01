# coding=utf-8

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import options, define
from handler import handlers

define("port", default=19000, help="本地监听端口", type=int)
define("DEBUG", default=True, help="是否开启debug模式", type=bool)
define("TEST",default=False,help="测试服务器，支持跨域访问,推送测试模式",type=bool)
tornado.options.parse_command_line()


application = tornado.web.Application(
    handlers=handlers,
    TEST = options.TEST,
    debug = options.DEBUG,
    compiled_template_cache = True,
    static_hash_cache = True,
    autoreload = True
)
application.listen(options.port)
ioloop = tornado.ioloop.IOLoop.current()

ioloop.start()

