import pyxb

import d1_common.types.dataoneTypes_v2_0 as v2
import d1_common.types.dataoneTypes_v1_1 as v11
import d1_common.types.dataoneTypes as v1

a = """<?xml version="1.0" ?>
<ns1:objectInfo xmlns:ns1="http://ns.dataone.org/service/types/v1">
  <identifier>__invalid_test_object__81e0e944-bf2d-11e0-a5cd-8122f1474081</identifier>
  <formatId>CF-1.2</formatId>
  <checksum algorithm="MD5">9d7d2447d5e1e37b647ad7c836f9a1b950f4d950</checksum>
  <dateSysMetadataModified>2011-08-05T06:38:19.532139</dateSysMetadataModified>
  <size>1772</size>
</ns1:objectInfo>
"""

try:
  print v2.CreateFromDocument(a)
except pyxb.ValidationError as e:
  print(e.details())
