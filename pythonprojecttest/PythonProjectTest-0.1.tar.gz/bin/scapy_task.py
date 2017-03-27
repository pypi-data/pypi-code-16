#! /usr/bin/env python
import sys
from scapy.all import *

#request/reply eth2
p=Ether(src='1c:bd:b9:d6:72:2f', dst='ec:e5:55:01:2b:37')/Dot1Q(vlan=200,prio=7)/IP(dst='1.1.1.2', src='1.1.1.1')/ICMP()
sendp(p,iface="eth2")
p.show()

#request sent on eth2 / reply received on eth1
p=Ether(src='80:1f:02:4c:2c:a5', dst='ec:e5:55:01:2b:37')/Dot1Q(vlan=200,prio=7)/IP(dst='1.1.1.2', src='15.1.1.75')/ICMP()
sendp(p,iface="eth2")
p.show()

#UDP packet forwarded by eagle back to the PC (eth3 --> eth1; 1/6 --> 1/4 )
p=Ether(src='80:1f:02:4c:2c:a5', dst='ec:e5:55:01:2b:36')/IP(dst='2.2.2.2', src='15.1.1.75')/UDP(dport=53)
sendp(p,iface="eth3")
p.show()
