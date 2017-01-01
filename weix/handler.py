from tornado.web import RequestHandler
import tornado
import hashlib
import json
import datetime
import string
import random
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient,HTTPError,HTTPRequest
import config
import tornado.gen
import time
import functools

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def parseWeixin(xmlstr):
    lines = xmlstr.split('\n')[1:-2]
    res = {'result_code':'','return_msg':'','return_code':'','err_code':'','err_code_des':''}
    for line in lines:
        end = line.find('>')
        code = line[1:end]
        for key in res.keys():
            if code == key:
                start = line.find('[CDATA[')
                end = line.find(']]><')
                value = line[start+7:end]
                res[key]=value
    return res
       

def generateWXParam(openid, amount):
    kv = {}
    date = datetime.datetime.now().strftime("%Y%m%d")
    config.num += random.randint(10,1000)
    mch_id = "1426868602"
    kv['mch_id'] = mch_id
    kv['mch_billno'] = mch_id + date +str(config.num)
    kv['wxappid'] = "wxappid"
    kv['send_name'] = "send_name"
    kv['re_openid'] = openid
    kv['total_amount'] = str(amount)
    kv['total_num'] = "1"
    kv['wishing'] = "wishing"
    kv['client_ip']="client_ip"
    kv['act_name'] = "act_name"
    kv['remark'] = "remark"
    kv['nonce_str'] = id_generator(30)
    stringA = ""
    for key, value in sorted(kv.items()):
        stringA +=(key+"="+value+"&")

    secretKey = "secretKey"
    stringA +=("key="+secretKey)
    sign  = hashlib.md5(stringA.encode()).hexdigest().upper()
    kv['sign'] = sign
    strr= "<xml>\n"
    for (key, value) in kv.items():
        strr+=('<{}><![CDATA[{}]]></{}>\n'.format(key,  value,key))
    strr+="</xml>"
    return strr

class TimeHandler(RequestHandler):
    """
    接收管理员命令，设置时间延迟
    参数：{"turn":turn, "timeDelay":timeDelay, "token":token}
    """     
    async def post(self):
        json_body = json.loads(self.request.body.decode('utf-8'))
        token=json_body['token']
        if token != config.token:
            await self.db.add_log("openid","admin time command",self.request.body.decode('utf-8') +"\n"+"token err")
            self.finish('code err')
            return
        config.turn = int(json_body['turn'])
        config.timeDelay = int(json_body['timeDelay'])
        config.delayFrom = int(time.time())
        self.finish('OK')
        await self.db.add_log ("openid","admin time command",self.request.body.decode('utf-8') +"\n"+"OK")
    @property
    def db(self):
        return self.settings['db']

class FinishHandler(RequestHandler):
    @property
    def db(self):
        return self.settings['db']
    async def post(self):
        json_body = json.loads(self.request.body.decode('utf-8'))
        token=json_body['token']
        sent = json_body['sent']
        if token != config.token:
            await self.db.add_log("openid","admin time command",self.request.body.decode('utf-8') +"\n"+"token err")
            self.finish('code err')
            return
        config.timeDelay = -1
        await self.notifyTimeServer()
        # sent the remaining redpackage
        if sent:
            print("即将发送所有剩余红包")
            await tornado.gen.sleep(5)
            print("开始发红包")  
            await sentRemaining()
            self.finish("remaining package sent")
            return
        self.finish("OK")

    async def sendRemaining(self):
        newList = config.getNewList()
        for amount in config.redPackagePools[config.turn-1]:
            print("红包发送中")
            if len(newList) == 0:
                return 
            index = randint(0, len(newList)-1)
            openid = newList.pop(index)
            await sendRedPackage(openid, int(amount*100))
    


    async def sendRedPackage(self, openid, amount):
        await self.db.add_log(openid,"try send RedPackage", "retry_Time :" + "none")
        url = "https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack"
        strr = generateWXParam(openid, amount)
        request = HTTPRequest(url = url, method = "POST", body = strr,   client_key="/home/coco/cert/apiclient_key.pem",
            ca_certs="/home/coco/cert/rootca.pem",  client_cert="/home/coco/cert/apiclient_cert.pem")
        client = AsyncHTTPClient()

        try:
            response = await client.fetch(request)
            res = parseWeixin(response.body.decode('utf-8'))
            await self.db.add_log(openid,"send RedPackage response", res)
            if res['return_code'] == 'SUCCESS' and res['result_code']=='SUCCESS' :
                config.hasSent[config.turn-1][openid] = amount/100.0
                await self.db.add_order(openid,config.turn,amount/100.0,"Sent")
            else :
                config.sendPackageResponseError += 1
                await self.db.add_order(openid,config.turn,amount/100.0,"NotSent")
        except Exception as e:
            await self.db.add_log(openid,"send RedPackage response", "redpackage Callback failed")
            config.sendPackageError += 1


    async def notifyTimeServer(self):
        strr = json.dumps( {"turn":config.turn, "token":config.token})
        request = HTTPRequest(url = config.timeUrl, method = "POST", body = strr)
        await self.db.add_log("","notify Time server", strr)
        client = AsyncHTTPClient()
        try:
            response = await client.fetch(request)
            await self.db.add_log("","notify Time server response", response.body.decode('utf-8'))
        except Exception:
            await self.db.add_log("","notify Time server response", "response error")



class RedHandler(RequestHandler):
#存储已发出红包信息:await self.db.add_order(id,波数,金额,got or sent)
#存储log:await self.db.add_log(code,content)
    def giveRedPackage(self):
        return random.randint(0,40) < 40

    def noRedPackage(self):
        errstr = json.dumps({"code":-1,"status":"fail"})
        self.add_header('Access-Control-Allow-Origin','http://yourcompany.com')
        self.finish(errstr)




    @property
    def db(self):
        return self.settings['db']


    async def notifyTimeServer(self):
        strr = json.dumps( {"turn":config.turn, "token":config.token})
        request = HTTPRequest(url = config.timeUrl, method = "POST", body = strr)
        await self.db.add_log("","notify Time server", strr)
        client = AsyncHTTPClient()
        try:
            response = await client.fetch(request)
            await self.db.add_log("","notify Time server response", response.body.decode('utf-8'))
        except Exception:
            await self.db.add_log("","notify Time server response", "response error")

    async def sendRedPackage(self):
        await self.db.add_log(self.openid,"try send RedPackage", "retry_Time :" + str(self.retry))
        url = "https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack"
        strr = generateWXParam(self.openid, self.amount)
        request = HTTPRequest(url = url, method = "POST", body = strr,   client_key="/home/coco/cert/apiclient_key.pem",
            ca_certs="/home/coco/cert/rootca.pem",  client_cert="/home/coco/cert/apiclient_cert.pem")
        client = AsyncHTTPClient()

        try:
            response = await client.fetch(request)
            res = parseWeixin(response.body.decode('utf-8'))
            await self.db.add_log(self.openid,"send RedPackage response", res)
            if res['return_code'] == 'SUCCESS' and res['result_code']=='SUCCESS' :
                config.hasSent[config.turn-1][self.openid] = self.amount/100.0
                await self.db.add_order(self.openid,config.turn,self.amount/100.0,"Sent")
            else :
                config.sendPackageResponseError += 1
                await self.db.add_order(self.openid,config.turn,self.amount/100.0,"NotSent")
        except Exception as e:
            await self.db.add_log(self.openid,"send RedPackage response", "redpackage Callback failed")
            config.sendPackageError += 1
            if(self.retry>1):
                 return
            self.retry += 1;
            delay_time = self.retry*6
            await self.db.add_log(self.openid,"send RedPackage retry", "start sleep: " + delay_time)
            await tornado.gen.sleep(delay_time)  
            await self.db.add_log(self.openid,"send RedPackage retry", "end sleep")
            await self.sendRedPackage()

    async def get(self):
        if config.timeDelay == -1:
            #print("timeDelay equals -1")
            self.noRedPackage()
            return
        remainingTime = config.timeDelay + config.delayFrom - time.time()
        if remainingTime > 0 :
            self.noRedPackage()
            #print("remaing Time")
            return
        
        if not self.giveRedPackage():
            self.noRedPackage()
            return
        #print('start query code')
        code = self.get_query_argument("code", None)
        if(code == None):
            self.noRedPackage()
            return
        url="https://api.weixin.qq.com/sns/oauth2/access_token?appid={0}&secret={1}&code={2}&grant_type=authorization_code".format("appid","secret",code)

        http_client = AsyncHTTPClient()
        #response = http_client.fetch(url,callback=self.openidCallback)

        jsonstr = {}
        try:
            response = await http_client.fetch(url)
            jsonstr = json.loads(response.body.decode('utf-8'))
        except Exception as e:
            config.fetchCodeError += 1
            await self.db.add_log("null", "fetch code error", e)
            self.noRedPackage()
            return

        if not "openid" in jsonstr :
            self.noRedPackage()
            return
        self.openid = jsonstr["openid"]

        # 检测当前openid本轮是否抢到过红包
        if self.openid in config.GottenIds:
            self.noRedPackage()
            return

        amount = config.redPackagePools[config.turn-1].pickOne()

        if(amount == -1):
            # 红包都发完了，向时间服务器发请求
            await self.db.add_log("","all redpackage send finish","")
            self.noRedPackage()
            config.timeDelay = -1
            await self.notifyTimeServer()
            return

        config.hasGotten[config.turn-1][self.openid] = amount
        config.GottenIds.append(self.openid)
        await self.db.add_order(self.openid,config.turn,amount,"Gotten")
        self.amount = int(amount*100); # 微信红包参数 以分为单位

        id={ 'code':0,'amount':amount,'status':'success'}
        successstr = json.dumps(id)
        #await self.db.add_order(id)
        self.add_header('Access-Control-Allow-Origin','http://your_company.com')
        self.finish(successstr)

        self.retry = 0
        await self.sendRedPackage()
  
def listToDict(list):
    dictt = {}
    for key in list:
        dictt[key] = dictt.get(key,0)+1
    return dictt   

class ConfigHandler(RequestHandler):
    def get(self):
        dictt = {}
        if config.timeDelay == -1 :
            # time not known
            dictt = {"remainingTime":"unknown",  "turn":config.turn}
        else:
            remainingTime = config.timeDelay + config.delayFrom - time.time()
            if remainingTime > 0 :
                dictt = {"remainingTime":int(remainingTime), "turn":config.turn}
            else :
                dictt = {"remainingTime":"redpackage ing",  "turn":config.turn}

        dictt["fetchCodeError"] = config.fetchCodeError
        dictt["sendPackageError"] = config.sendPackageError
        dictt["sendPackageResponseError"] = config.sendPackageResponseError

        dictt["pool1"] = listToDict(config.redPackagePools[0].pool)
        dictt["pool2"] = listToDict(config.redPackagePools[1].pool)
        dictt["pool3"] = listToDict(config.redPackagePools[2].pool)
        dictt['hasGotten1'] = functools.reduce(lambda x,y:x+y,config.hasGotten[0].values(),0)
        dictt['hasSent1'] = functools.reduce(lambda x,y:x+y,config.hasSent[0].values(),0)
        dictt['hasGotten2'] = functools.reduce(lambda x,y:x+y,config.hasGotten[1].values(),0)
        dictt['hasSent2'] = functools.reduce(lambda x,y:x+y,config.hasSent[1].values(),0)
        dictt['hasGotten3'] = functools.reduce(lambda x,y:x+y,config.hasGotten[2].values(),0)
        dictt['hasSent3'] = functools.reduce(lambda x,y:x+y,config.hasSent[2].values(),0)
        self.finish(json.dumps(dictt))
        return
        



handlers = []
handlers += [
        (r'/red', RedHandler),
        (r'/time', TimeHandler),
        (r'/config',ConfigHandler),
        (r'/finish', FinishHandler)
]

