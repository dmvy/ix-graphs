#!/usr/bin/python

#import yapsnmp

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1902 import Integer, IpAddress, OctetString
import time
import string
import socket
import csv
import rrdtool
import os

def rrd_create(rrd_file):
    if not os.path.isfile(rrd_file):
        rrdtool.create(rrd_file,
                        "--step", "30sec",
                        "DS:in:COUNTER:60:0:10000000000",
                        "DS:out:COUNTER:60:0:10000000000",
                        "RRA:AVERAGE:0.5:1:366",
                        "RRA:AVERAGE:0.5:1:2880",
                        "RRA:AVERAGE:0.5:10:8064",
                        "RRA:AVERAGE:0.5:60:17520",
                        "RRA:AVERAGE:0.5:600:17520",
                        "RRA:MAX:0.5:1:2880",
                        "RRA:MAX:0.5:10:8064",
                        "RRA:MAX:0.5:60:17520",
                        "RRA:MAX:0.5:600:17520",
                        "RRA:LAST:0.5:1:2880"
                       )

def rrd_update(rrd_file, in_counter, out_counter):
    rrdtool.update(rrd_file, "N:%s:%s" % (in_counter,out_counter))

asnum = csv.reader(open('peers.as','rb'), delimiter=';')
d={}
for row in asnum:
    d[row[0]]=row

ip='10.0.0.1'
comm='public'
interface=668
l2_int=(508,509,510,511)
l2_vlan=600

oid=(1,3,6,1,2,1,4,22,1,2,interface)

res = (errorIndication, errorStatus, errorIndex, varBindTable) = cmdgen.CommandGenerator().nextCmd(
    cmdgen.CommunityData('test-agent', comm, 1),
    cmdgen.UdpTransportTarget((ip, 161)),
    oid
)

if errorIndication:
    print errorIndication
else:
    if errorStatus:
        print '%s at %s\n' % (
            errorStatus.prettyPrint(),
            errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
            )
    else:
        for varBindTableRow in varBindTable:
            for name, val in varBindTableRow:
                arp_ip = '%s.%s.%s.%s' % (name[11],name[12],name[13],name[14])
#                if (arp_ip == '194.85.107.65'): break
#                arp_name = socket.gethostbyaddr(arp_ip)
                oid_mac=tuple(map(int,['%d' % ord(x) for x in val]))

                in_bytes=0
                out_bytes=0
                for interface in l2_int:
                    # in bytes
                    oid_in=(1,3,6,1,4,1,2636,3,23,1,1,1,3,interface,l2_vlan)+oid_mac
                    res_in = (errorIndication2, errorStatus2, errorIndex2, varBindTable2) = cmdgen.CommandGenerator().getCmd(
                        cmdgen.CommunityData('test-agent', comm, 1),
                        cmdgen.UdpTransportTarget((ip, 161)),
                        oid_in
                    )
                    tmp02=varBindTable2[0]
                    if not (tmp02[1]):
                        in_bytes=0
                    else:
                        in_bytes=in_bytes+tmp02[1]
                    # out bytes
                    oid_out=(1,3,6,1,4,1,2636,3,23,1,1,1,5,interface,l2_vlan)+oid_mac
                    res_out = (errorIndication3, errorStatus3, errorIndex3, varBindTable3) = cmdgen.CommandGenerator().getCmd(
                        cmdgen.CommunityData('test-agent', comm, 1),
                        cmdgen.UdpTransportTarget((ip, 161)),
                        oid_out
                    )
                    tmp03=varBindTable3[0]
                    if not (tmp03[1]):
                        out_bytes=0
                    else:
                        out_bytes=out_bytes+tmp03[1]
                print '%s %s %s' % (arp_ip ,in_bytes,out_bytes)
#                print d.get(arp_ip,'null')
                rrd_file='rrd/'+arp_ip+'.rrd'
                png_file='png/'+arp_ip+'.png'
                rrd_create(rrd_file)
                rrd_update(rrd_file,in_bytes,out_bytes)
                rrdtool.graph(png_file,
	'--imgformat','PNG',
	'--title="%s"' % arp_ip,
	'--height','150',
	'--width','400',
	'--end','now',
	'--start','end-24h',
	'--slope-mode',
	'--base=1000',
	'--lower-limit=0',
	'--alt-autoscale-max',
	'--vertical-label=bitspersecond',
	'DEF:in=%s:in:AVERAGE'%rrd_file,
	'DEF:out=%s:out:AVERAGE'%rrd_file,
	'CDEF:inb=in,8,*',
	'CDEF:outb=out,8,*',
	'AREA:inb#00CF00FF:in',
	'LINE1:outb#0000CFFF:out',
	'GPRINT:inb:AVERAGE:in_avg\:%6.2lf%s',
	'GPRINT:outb:AVERAGE:out_avg\:%6.2lf%s'
                )

                png_file='png/'+arp_ip+'_month.png'
                rrdtool.graph(png_file,
        '--imgformat','PNG',
        '--title="%s"' % arp_ip,
        '--height','150',
        '--width','400',
        '--end','now',
        '--start','end-30d',
        '--slope-mode',
        '--base=1000',
        '--lower-limit=0',
        '--alt-autoscale-max',
        '--vertical-label=bitspersecond',
        'DEF:in=%s:in:AVERAGE'%rrd_file,
        'DEF:out=%s:out:AVERAGE'%rrd_file,
        'CDEF:inb=in,8,*',
        'CDEF:outb=out,8,*',
        'AREA:inb#00CF00FF:in',
        'LINE1:outb#0000CFFF:out',
        'GPRINT:inb:AVERAGE:in_avg\:%6.2lf%s',
        'GPRINT:outb:AVERAGE:out_avg\:%6.2lf%s'
)
