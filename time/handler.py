from tornado.web import RequestHandler
import datetime
import config
import json
import time


class TimeHandler(RequestHandler):
    """
    通知网页端，目前的红包状态
    参数： 无
    返回结果：{"flag":flag, "time":time, "turn":turn}
    flag : 当前是否正在抢红包, 0:正在抢红包，1：正在倒计时， 2：开抢时间未知
    turn : 当前第几轮
    time : 还有多久开抢， -1表示时间未知
    """
    def get(self):
        print("get")
        self.add_header('Access-Control-Allow-Origin','http://aaa.bbb.com')
        if config.timeDelay == -1 :
            # time not known
            dictt = {"flag":2,  "turn":config.turn}
            self.finish(json.dumps(dictt))
            return
        remainingTime = config.timeDelay + config.delayFrom - time.time()
        if remainingTime > 0 :
            dictt = {"flag": 1, "time":remainingTime, "turn":config.turn}
            self.finish(json.dumps(dictt))
        else :
            dictt = {"flag":0,  "turn":config.turn}
            self.finish(json.dumps(dictt))
       
    """
    接收管理员命令，设置时间延迟
    参数：{"turn":turn, "timeDelay":timeDelay, "token":token}
    """     
    def post(self):
        print(self.request.body.decode('utf-8'))
        json_body = json.loads(self.request.body.decode('utf-8'))
        token=json_body['token']
        if token != config.token:
            self.finish('code err')
            return
        print(json_body)
        config.turn = int(json_body['turn'])
        config.timeDelay = int(json_body['timeDelay'])
        config.delayFrom = time.time()
        self.finish('OK')
               
class FinishHandler(RequestHandler):
    """
    接收微信服务器命令，关闭当前波
    参数：{"turn":turn, "token":token}
    """
    def post(self):
        print(self.request.body.decode('utf-8'))
        json_body = json.loads(self.request.body.decode('utf-8'))
        token=json_body['token']
        if token != config.token:
            self.finish('code err')
            return
        if config.turn != json_body['turn']:
            self.finish('turn err')
        config.timeDelay = -1
        config.turn += 1
        self.finish("ok")

class ConfigHandler(RequestHandler):
    def get(self):
        if config.timeDelay == -1 :
            # time not known
            dictt = {"remainingTime":"unknown",  "turn":config.turn}
            self.finish(json.dumps(dictt))
            return
        #print("{0}  {1}  {2}".format(type(config.timeDelay),type(config.delayFrom), type(time.time())))
        remainingTime = config.timeDelay + config.delayFrom - time.time()
        if remainingTime > 0 :
            dictt = {"flag": 1, "remainingTime":int(remainingTime), "turn":config.turn}
            self.finish(json.dumps(dictt))
        else :
            dictt = {"remainingTime":"redpackage ing",  "turn":config.turn}
            self.finish(json.dumps(dictt))
 
handlers = []
handlers += [
        (r'/time', TimeHandler),
        (r'/finish', FinishHandler),
        (r'/config', ConfigHandler)
]

