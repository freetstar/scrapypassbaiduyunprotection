#-*- coding:utf-8 -*-
#!/usr/bin/env python2.7
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from pyv8 import PyV8
import re
import time

import requests
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


#访问首页时，接受服务器发送来的set-cookie中的__cfduif的cookie
s = requests.session()
r = s.get("http://www.vegnet.com.cn",headers = headers)
presetcookie = r.headers['set-cookie']
sentcookie1st = dict(__cfduid = presetcookie.split(";")[0].split("=")[1])

###########解析页面中的js代码，放到v8中执行##################################
from bs4 import BeautifulSoup
soup = BeautifulSoup(r.text,'lxml')
pass_value = soup.find(attrs={'name': 'pass'}).get('value')
jschl_vc_value = soup.find(attrs={'name': 'jschl_vc'}).get('value')

#tempstr 存储以下形式的字符串
#rkJsjKz.KvWrlLpzwg-=!+[]+!![]+!![]+!![]+!![]+!![]+!![];rkJsjKz.KvWrlLpzwg*=+((!+[]+!![]+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]));rkJsjKz.KvWrlLpzwg+=+((!+[]+!![]+!![]+!![]+[])+(!+[]+!![]+!![]));rkJsjKz.KvWrlLpzwg-=+((!+[]+!![]+!![]+[])+(+!![]))
tempstr =''
a = re.search('var s,t,o,p,b,r,e,a,k,i,n,g,f, (\w+)={"(\w+)":(.*)};',r.text)
dictname, key, value  = a.group(1), a.group(2), a.group(3)
a = re.search(';(.*;)a\.value',r.text)
tempstr = dictname +'.'+key + '=' + value +";"+ a.group(1)

#进入v8
ctxt = PyV8.JSContext()
ctxt.enter()
#拼凑js代码
oo = "(function(){var "+ dictname + "={'"+ key +"':''};"+tempstr+"return "+dictname+"."+key+";})"
func = ctxt.eval(str(oo))
#对应a.value = parseInt(rkJsjKz.KvWrlLpzwg, 10) + t.length中的t.lendth也就是域名的长度
jschl_answer_value = str(func()+len("www.vegnet.com.cn"))

payload = {
    'pass':pass_value,
    'jschl_vc':jschl_vc_value,
    'jschl_answer':jschl_answer_value,

}

#很关键，需要进行5秒钟休眠
time.sleep(5)

requesturl = "http://www.vegnet.com.cn/cdn-cgi/l/chk_jschl"
#allow_redirects ＝ False不要让requests来自动处理302的跳转
r = requests.get(requesturl,allow_redirects=False,cookies = sentcookie1st, headers= headers, params = payload )
print r.status_code
#获取cf_clearance这个cookie
presetcookie = r.headers['set-cookie']
sentcookie2nd = {'cf_clearance':presetcookie.split(";")[0].split("=")[1]}

r = requests.get("http://www.vegnet.com.cn/",cookies = sentcookie2nd, headers = headers)
print r.status_code
