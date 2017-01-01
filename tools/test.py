import xml.etree.ElementTree as ET
xmlstr = """<xml>
<return_code><![CDATA[SUCCESS]]></return_code>
<return_msg><![CDATA[发放成功]]></return_msg>
<result_code><![CDATA[SUCCESS]]></result_code>
<err_code><![CDATA[SUCCESS]]></err_code>
<err_code_des><![CDATA[发放成功]]></err_code_des>
<mch_billno><![CDATA[1426868602201612241103426000]]></mch_billno>
<mch_id><![CDATA[mch_id]]></mch_id>
<wxappid><![CDATA[wxappid]]></wxappid>
<re_openid><![CDATA[oSEhFwzi0ALRS__AHNUalVl_y104]]></re_openid>
<total_amount>100</total_amount>
<send_listid><![CDATA[1000041701201612243000065657052]]></send_listid>
</xml>
"""
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
print(parseWeixin(xmlstr))
