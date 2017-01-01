import json 
import urllib.request


time_domain = 'http://time_domain.com:19000/'
weix_domain = 'http://weix_domain.com:18000/'
token = "redpackage token"

def sendTime(turn, timeDelay):
	values = {"turn":turn, "timeDelay":timeDelay, "token":token}
	data = str.encode(json.dumps(values))

	url_time = time_domain + 'time'
	req = urllib.request.Request(url_time, data)
	response = urllib.request.urlopen(req)
	the_page = response.read()
	time_res = the_page.decode("utf8")

	url_weix =  weix_domain + 'time'
	req = urllib.request.Request(url_weix, data)
	response = urllib.request.urlopen(req)
	the_page = response.read()
	weix_res = the_page.decode("utf8")

	return (time_res, weix_res)

def getConfig():
	url_time = time_domain + 'config'
	url_weix = weix_domain + 'config'
	strr = "time_config:\n"
	try:
		fp = urllib.request.urlopen(url_time)
		time_config = fp.read().decode("utf8")
		fp.close()
		json_time = json.loads(time_config)	
		strr+= ("turn : {0}\nremainingTime : {1}\n\n".format(json_time['turn'], json_time['remainingTime']))
	except Exception as e:
		strr += str(e)

	strr += 'weix_config\n'
	try:
		fp = urllib.request.urlopen(url_weix)
		weix_config = fp.read().decode("utf8")
		fp.close()
		json_weix = json.loads(weix_config)
		
		strr += ("turn : {0}\nremainingTime : {1}\n".format(json_weix['turn'], json_weix['remainingTime']))
		strr += "\nturn1\n"
		summ = 0
		for key,value in json_weix['pool1'].items():
			strr+=("{0} : {1}    ".format(key,value))
			summ += float(key)*float(value)
		strr += "sum : {0}".format(summ)
		strr += "\n   hasGotten: {0} ".format(json_weix['hasGotten1'])
		strr += "   hasSent: {0} ".format(json_weix['hasSent1'])
		
		strr += "\nturn2\n"
		summ = 0
		for key,value in json_weix['pool2'].items():
			strr+=("{0} : {1}    ".format(key,value))
			summ += float(key)*float(value)
		strr += "sum : {0}".format(summ)
		strr += "   hasGotten: {0} ".format(json_weix['hasGotten2'])
		strr += "   hasSent: {0} ".format(json_weix['hasSent2'])
		strr += "\nturn3\n"
		summ = 0
		for key,value in json_weix['pool3'].items():
			strr+=("{0} : {1}    ".format(key,value))
			summ += float(key)*float(value)
		strr += "sum : {0}".format(summ)
		strr += "   hasGotten: {0} ".format(json_weix['hasGotten3'])
		strr += "   hasSent: {0} ".format(json_weix['hasSent3'])


		strr += "\n\n   fetchCodeError: {0} ".format(json_weix['fetchCodeError'])
		strr += "   sendPackageError: {0} ".format(json_weix['sendPackageError'])
		strr += "   sendPackageResponseError: {0} ".format(json_weix['sendPackageResponseError'])
	except Exception as e:
		strr += str(e)
	return strr


def finishTurn(sent):
	res = ""
	try:
		values = {"token":token,"sent":sent}
		data = str.encode(json.dumps(values))

		url_finish = weix_domain + 'finish'
		req = urllib.request.Request(url_finish, data)
		response = urllib.request.urlopen(req)
		the_page = response.read()
		res = the_page.decode("utf8")
	except Exception as e:
		res = str(e)
	return res