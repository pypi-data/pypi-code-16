from ciscoconfparse import CiscoConfParse
from ccp_util import CiscoRange

print CiscoRange('1,2-4,5', result_type=int).remove('3-4')

lines = ['!',
    'interface GigabitEthernet 1/1',
    ' switchport mode trunk',
    ' switchport trunk allowed vlan none',
    ' switchport trunk allowed vlan add 2-4094',
    ' switchport trunk native vlan 911',
    '!',
]
cfg = CiscoConfParse(lines, factory=True)
intf_obj = cfg.find_objects('^interface')[0]
print intf_obj.trunk_vlans_allowed.as_list

