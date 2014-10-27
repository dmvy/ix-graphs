#!/usr/bin/python

import urllib
import lxml.html
#import re, cymruwhois
from subprocess import Popen
from subprocess import PIPE
#import subprocess

load = 'load'
enc_data = urllib.urlencode([('Submit', 1), ('query', 'summary'), ('rtr', 'msk-rs1.ripn.net')])
page = urllib.urlopen('http://www.msk-ix.ru/network/lookingglass.html', enc_data)
#print page.read()
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


for link in doc.cssselect('pre'):
#    print link.text
    for inform in link.text.split('\n'):
        res = inform.split()
        if len(res)>=7:
            if len(res[0]) > 11:
                if ( res[0][0:10] == '193.232.24'):
                    print res[0], res[2]
                    if ( res[0][0:9] == '193.232.24' ): continue
                    as_name=Popen('whois -F -r -T aut-num as'+res[2]+'|grep "*aa:"|cut -d ":" -f 2',stdout=PIPE,shell=True).stdout.readlines()
                    as_descr=Popen('whois -F -r -T aut-num as'+res[2]+'|grep "*de:"|cut -d ":" -f 2',stdout=PIPE,shell=True).stdout.readlines()
                    if ( as_name and as_descr ):
                        print as_name[0][1:-1]
                        print as_descr[0][1:-1]
                        print '%s;%s;%s;%s' % (res[0], res[2], as_name[0][1:-1], as_descr[0][1:-1])
                        peers.write('%s;%s;%s;%s\n' % (res[0], res[2], as_name[0][1:-1], as_descr[0][1:-1]))
                        index.write('<div>ip: %s; AS%s; as-name: %s; as-descr: %s</div>\n' % 
                                   (res[0], res[2], as_name[0][1:-1], as_descr[0][1:-1]))
                    else:
                        print '%s;%s' % (res[0], res[2])
                        peers.write('%s;%s\n' % (res[0], res[2]))
                        index.write('<div>ip: %s; AS%s</div>\n' %
                                   (res[0], res[2]))
                    index.write('<img src=png/%s.png />' % res[0])
                    index.write('<img src=png/%s_month.png />\n' % res[0])
                else:
                    continue

index.write("""</center>
</body>
</html>""")

index.close()
peers.close()

