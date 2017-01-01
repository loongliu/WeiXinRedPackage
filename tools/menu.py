from urllib import request, parse

# 设置微信服务号菜单

import requests
import json
url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format("appid","secret")
r = requests.get(url)
print(r.text)
j = json.loads(r.text)
token = j['access_token']
print(token)
url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token={0}".format(token)
strr = ' {"button":[{"type":"view", "name":"NAME","url":"your_url.com"}]}'
r = requests.post(url,data = strr.encode('utf-8'))
print(r.text)
