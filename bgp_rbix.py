#!/usr/bin/python

import urllib2
import urllib
import cookielib
import lxml.html
#import re, cymruwhois
from subprocess import Popen
from subprocess import PIPE

cookies = cookielib.CookieJar()
page_get = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
page_get.open('http://www.rb-ix.ru/lg')
post_cookie = cookies._cookies['www.rb-ix.ru']['/']['csrftoken'].value
enc_data = urllib.urlencode([('action', 'neighbor'), ('additional_data', ''), ('csrfmiddlewaretoken', post_cookie), ('prefix', '')])
page = page_get.open('http://www.rb-ix.ru/lg', enc_data)

doc = lxml.html.document_fromstring(page.read())
peers = open('peers.as','w')
index = open('index.html','w')

index.write("""<html>
<head>
<title>SpeedTest</title>
<meta http-equiv="content-type" content="text/html; charset=utf-8" >
<meta http-equiv="refresh" content="1800">
</head>
<body>
<center>""")

ip=''
for link in doc.cssselect('tr.none td'):
    for inform in link.text.split('\n'):
        res=inform
        if ( res[0:8] == '185.1.0.' ):
            ip=res
        elif (ip != ''):
            asnum=res
            as_name=Popen('whois -F -r -T aut-num as'+asnum+'|grep "*aa:"|cut -d ":" -f 2',stdout=PIPE,shell=True).stdout.readlines()
            as_descr=Popen('whois -F -r -T aut-num as'+asnum+'|grep "*de:"|cut -d ":" -f 2',stdout=PIPE,shell=True).stdout.readlines()
            print '%s;%s;%s;%s' % (ip, asnum, as_name[0][1:-1], as_descr[0][1:-1])
            peers.write('%s;%s;%s;%s\n' % (ip, asnum, as_name[0][1:-1], as_descr[0][1:-1]))
            index.write('<div>ip: %s; AS%s; as-name: %s; as-descr: %s</div>' %
            (ip, asnum, as_name[0][1:-1], as_descr[0][1:-1]))
            index.write('<img src=png/%s.png />' % ip)
            index.write('<img src=png/%s_month.png />' % ip)
            ip = ''
        else:
            continue

index.write("""</center>
</body>
</html>""")

index.close()
peers.close()

