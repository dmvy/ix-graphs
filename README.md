Данная программа показывает загрузку на интерфейсе по mac-адресам.

Конфигурирование:

Указываем ip-адрес роутера
ip='10.0.0.1'

SNMP-community
comm='public'

l3-интерфейс: необходимо указать SNMP ifIndex
user@border# run show interfaces ae1.600 extensive 
  Logical interface ae1.600 (Index 336) (SNMP ifIndex 668) (Generation 389)
    Description: peer-ix
    Flags: SNMP-Traps 0x0 VLAN-Tag [ 0x8100.600 ]  Encapsulation: ENET2
    Bandwidth: 10000mbps
    Statistics        Packets        pps         Bytes          bps
    Bundle:
        Input :  864855965976     107168 868946046694130    851303656
        Output:  352107561269      54422 201862042211671    245713624
    Link:
      xe-0/0/0.600
        Input :  216158910309      21981 217186853175623    165960760
        Output:   87942433149      11590 50452126542336     60941216
      xe-0/0/1.600
        Input :  216542322087      26833 217572348624109    199386840
        Output:   88443541251      16702 50802593087102     91618456
      xe-0/0/2.600
        Input :  216139762785      26434 217376623008085    225913648
        Output:   87748408824      13450 50107684141036     43833872
      xe-0/0/3.600
        Input :  216014970795      31920 216810221886313    260042408
        Output:   87973178045      12680 50499638441197     49320080
interface=668

физический интерйес или интерфейсы в случае link-agg
user@border# run show interfaces xe-0/0/0   
Physical interface: xe-0/0/0, Enabled, Physical link is Up
  Interface index: 139, SNMP ifIndex: 508
Physical interface: xe-0/0/1, Enabled, Physical link is Up
  Interface index: 140, SNMP ifIndex: 509
Physical interface: xe-0/0/2, Enabled, Physical link is Up
  Interface index: 141, SNMP ifIndex: 510
Physical interface: xe-0/0/3, Enabled, Physical link is Up
  Interface index: 142, SNMP ifIndex: 511
l2_int=(508,509,510,511)

И самое простое - указать номер vlan
l2_vlan=600

После этого ставим в crontab скрипты и статистика уже начнет набираться. RRD настроен на съем данных 2 раза в минуту.
Путь до скрипта указываем свой.
crontab -e
*       *       *       *       *       cd /home/user/develop/juno_l2/; ./generate.py > /dev/null 2>&1
*       *       *       *       *       sleep 30; cd /home/user/develop/juno_l2/; ./generate.py > /dev/null 2>&1
Т.к. скрипт сначала собирает arp-таблицу и по ней уже из нее извлекает мак-адреса для статистики, то желательно сделать nmap -sP -T5 195.64.0.0/24 на ту сеть, в которой идет пиринг на IX.

Для отображения нужно сгенерировать index.html скриптом bgp.py

