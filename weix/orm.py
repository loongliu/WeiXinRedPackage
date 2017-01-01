import bson
import copy
import datetime
def ObjectId(id):
    return bson.objectid.ObjectId(id)

class MongoOrm(object):
    def __init__(self, mongo_client):
        self.db = mongo_client
    async def add_order(self, openid,turn,rednum,flag):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
        dictt = {
        'openid':openid,
        'turn':turn,
        'rednum':rednum,
        'flag':flag,
        'date':date
        }
        result = await self.db.order.insert(dictt)
        result = await self.db.log.insert(dictt)
        return result;
        
    async def add_log(self,openid,code,content):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
        result = await self.db.log.insert({
        'openid':openid,
        'code':code,
        'content':content,
        'date':date
        })
        return result;
