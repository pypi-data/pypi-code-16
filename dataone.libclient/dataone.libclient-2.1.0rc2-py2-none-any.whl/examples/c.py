#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Stdlib
import datetime
import hashlib
import logging
import StringIO

# D1
import d1_common.types.dataoneTypes as dataoneTypes
import d1_client.mnclient_2_0
import d1_common.const
import d1_client.mnclient

# Config.

# The path to the file that will be uploaded as a Science Object.
SCIENCE_OBJECT_FILE_PATH = './my_test_object.bin'

# The identifier (PID) to use for the Science Object.
SCIENCE_OBJECT_PID = 'dataone_test_object_pid'

# The formatId to use for the Science Object. It should be the ID of an Object
# Format that is registered in the DataONE Object Format Vocabulary. The valid
# IDs can be retrieved from https://cn.dataone.org/cn/v1/formats.
SYSMETA_FORMATID = 'application/octet-stream'

# The DataONE subject to set as the rights holder of the created objects. The
# rights holder must be a subject that is registered with DataONE. Subjects are
# created in the DataONE identity manager at https://cn.dataone.org/cn/portal.
#
# By default, only the rights holder has access to the object, so access to the
# uploaded object may be lost if the rights holder subject is set to a
# non-existing subject or to a subject that is not prepared to handle the
# object.
SYSMETA_RIGHTSHOLDER = 'CN=First Last,O=Google,C=US,DC=cilogon,DC=org'

# BaseURL for the Member Node. If the script is run on the same server as the
# Member Node, this can be localhost.
MN_BASE_URL = 'https://dataone-test.researchworkspace.com/mn'
#MN_BASE_URL = 'https://localhost/mn'
#MN_BASE_URL = 'https://gmn.test.dataone.org/mn'

# Paths to the certificate and key to use when creating the object. If the
# certificate has the key embedded, the _KEY setting should be set to None. The
# Member Node must trust the certificate and allow access to MNStorage.create()
# for the certificate subject. If the target Member Node is a DataONE Generic
# Member Node (GMN) instance, see the "Using GMN" section in the documentation
# for GMN for information on how to create and use certificates. The information
# there may be relevant for other types of Member Nodes as well.
CERTIFICATE_FOR_CREATE = 'urn_node_mnTestRW/urn_node_mnTestRW.crt'
CERTIFICATE_FOR_CREATE_KEY = 'urn_node_mnTestRW/private/urn_node_mnTestRW.key'


def main():
  logging.basicConfig()
  logging.getLogger('').setLevel(logging.DEBUG)

  # Create a Member Node client that can be used for running commands against
  # a specific Member Node.
  client = d1_client.mnclient_2_0.MemberNodeClient_2_0(
    MN_BASE_URL, cert_pem_path=CERTIFICATE_FOR_CREATE,
    cert_key_path=CERTIFICATE_FOR_CREATE_KEY
  )
  # Get the bytes for the Science Object.
  science_object = open(SCIENCE_OBJECT_FILE_PATH, 'rb').read()
  # Create the System Metadata for the object that is to be uploaded. The
  # System Metadata contains information about the object, such as its
  # format, access control list and size.
  sys_meta = generate_system_metadata_for_science_object(science_object)
  # Create the object on the Member Node. The create() call takes an open
  # file-like object for the Science Object. Since we already have the data in a
  # string, we use StringIO. Another way would be to open the file again, with
  # "f = open(filename, 'rb')", and then pass "f". The StringIO method is more
  # efficient if the file fits in memory, as it already had to be read from disk
  # once, for the MD5 checksum calculation.
  client.create(SCIENCE_OBJECT_PID, StringIO.StringIO(science_object), sys_meta)
  print 'Object created successfully'


def generate_system_metadata_for_science_object(science_object):
  pid = SCIENCE_OBJECT_PID
  size = len(science_object)
  md5 = hashlib.md5(science_object).hexdigest()
  now = datetime.datetime.now()
  sys_meta = generate_sys_meta(pid, size, md5, now)
  return sys_meta


def generate_sys_meta(pid, size, md5, now):
  sys_meta = dataoneTypes.systemMetadata()
  sys_meta.identifier = pid
  sys_meta.formatId = SYSMETA_FORMATID
  sys_meta.size = size
  sys_meta.rightsHolder = SYSMETA_RIGHTSHOLDER
  sys_meta.checksum = dataoneTypes.checksum(md5)
  sys_meta.checksum.algorithm = 'MD5'
  sys_meta.dateUploaded = now
  sys_meta.dateSysMetadataModified = now
  sys_meta.accessPolicy = generate_public_access_policy()
  return sys_meta


def generate_public_access_policy():
  accessPolicy = dataoneTypes.accessPolicy()
  accessRule = dataoneTypes.AccessRule()
  accessRule.subject.append(d1_common.const.SUBJECT_PUBLIC)
  permission = dataoneTypes.Permission('read')
  accessRule.permission.append(permission)
  accessPolicy.append(accessRule)
  return accessPolicy


if __name__ == '__main__':
  main()
