from __future__ import absolute_import, unicode_literals, print_function, division

import json
import netmagus.form
import netmagus.netop

ta = netmagus.form.NetMagusFormTextArea(label='test label',description='test description')
testform = netmagus.form.NetMagusForm(componentlist=[ta])


print(ta.as_dict())
print(testform.as_list_of_dicts())


netop = netmagus.netop.NetMagusNetOpStep(initialForm=testform, description='netop description')

print(netop.as_dict())
print(json.dumps(netop.as_dict()))
