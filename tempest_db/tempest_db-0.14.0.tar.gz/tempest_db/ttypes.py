#
# Autogenerated by Thrift Compiler (0.9.3)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class DegreeFilterTypes:
  INDEGREE_MIN = 0
  INDEGREE_MAX = 1
  OUTDEGREE_MIN = 2
  OUTDEGREE_MAX = 3

  _VALUES_TO_NAMES = {
    0: "INDEGREE_MIN",
    1: "INDEGREE_MAX",
    2: "OUTDEGREE_MIN",
    3: "OUTDEGREE_MAX",
  }

  _NAMES_TO_VALUES = {
    "INDEGREE_MIN": 0,
    "INDEGREE_MAX": 1,
    "OUTDEGREE_MIN": 2,
    "OUTDEGREE_MAX": 3,
  }


class Node:
  """
  Attributes:
   - type
   - id
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'type', None, None, ), # 1
    (2, TType.STRING, 'id', None, None, ), # 2
  )

  def __init__(self, type=None, id=None,):
    self.type = type
    self.id = id

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.type = iprot.readString()
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.id = iprot.readString()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Node')
    if self.type is not None:
      oprot.writeFieldBegin('type', TType.STRING, 1)
      oprot.writeString(self.type)
      oprot.writeFieldEnd()
    if self.id is not None:
      oprot.writeFieldBegin('id', TType.STRING, 2)
      oprot.writeString(self.id)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.type is None:
      raise TProtocol.TProtocolException(message='Required field type is unset!')
    if self.id is None:
      raise TProtocol.TProtocolException(message='Required field id is unset!')
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.type)
    value = (value * 31) ^ hash(self.id)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class MonteCarloPageRankParams:
  """
  Attributes:
   - numSteps
   - resetProbability
   - maxIntermediateNodeDegree
   - minReportedVisits
   - maxResultCount
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'numSteps', None, None, ), # 1
    (2, TType.DOUBLE, 'resetProbability', None, None, ), # 2
    (3, TType.I32, 'maxIntermediateNodeDegree', None, 1000, ), # 3
    (4, TType.I32, 'minReportedVisits', None, None, ), # 4
    (5, TType.I32, 'maxResultCount', None, None, ), # 5
  )

  def __init__(self, numSteps=None, resetProbability=None, maxIntermediateNodeDegree=thrift_spec[3][4], minReportedVisits=None, maxResultCount=None,):
    self.numSteps = numSteps
    self.resetProbability = resetProbability
    self.maxIntermediateNodeDegree = maxIntermediateNodeDegree
    self.minReportedVisits = minReportedVisits
    self.maxResultCount = maxResultCount

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.numSteps = iprot.readI32()
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.DOUBLE:
          self.resetProbability = iprot.readDouble()
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I32:
          self.maxIntermediateNodeDegree = iprot.readI32()
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.I32:
          self.minReportedVisits = iprot.readI32()
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.I32:
          self.maxResultCount = iprot.readI32()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('MonteCarloPageRankParams')
    if self.numSteps is not None:
      oprot.writeFieldBegin('numSteps', TType.I32, 1)
      oprot.writeI32(self.numSteps)
      oprot.writeFieldEnd()
    if self.resetProbability is not None:
      oprot.writeFieldBegin('resetProbability', TType.DOUBLE, 2)
      oprot.writeDouble(self.resetProbability)
      oprot.writeFieldEnd()
    if self.maxIntermediateNodeDegree is not None:
      oprot.writeFieldBegin('maxIntermediateNodeDegree', TType.I32, 3)
      oprot.writeI32(self.maxIntermediateNodeDegree)
      oprot.writeFieldEnd()
    if self.minReportedVisits is not None:
      oprot.writeFieldBegin('minReportedVisits', TType.I32, 4)
      oprot.writeI32(self.minReportedVisits)
      oprot.writeFieldEnd()
    if self.maxResultCount is not None:
      oprot.writeFieldBegin('maxResultCount', TType.I32, 5)
      oprot.writeI32(self.maxResultCount)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.numSteps is None:
      raise TProtocol.TProtocolException(message='Required field numSteps is unset!')
    if self.resetProbability is None:
      raise TProtocol.TProtocolException(message='Required field resetProbability is unset!')
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.numSteps)
    value = (value * 31) ^ hash(self.resetProbability)
    value = (value * 31) ^ hash(self.maxIntermediateNodeDegree)
    value = (value * 31) ^ hash(self.minReportedVisits)
    value = (value * 31) ^ hash(self.maxResultCount)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class BidirectionalPPRParams:
  """
  Attributes:
   - relativeError
   - resetProbability
   - minProbability
  """

  thrift_spec = (
    None, # 0
    (1, TType.DOUBLE, 'relativeError', None, None, ), # 1
    (2, TType.DOUBLE, 'resetProbability', None, None, ), # 2
    (3, TType.DOUBLE, 'minProbability', None, None, ), # 3
  )

  def __init__(self, relativeError=None, resetProbability=None, minProbability=None,):
    self.relativeError = relativeError
    self.resetProbability = resetProbability
    self.minProbability = minProbability

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.DOUBLE:
          self.relativeError = iprot.readDouble()
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.DOUBLE:
          self.resetProbability = iprot.readDouble()
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.DOUBLE:
          self.minProbability = iprot.readDouble()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('BidirectionalPPRParams')
    if self.relativeError is not None:
      oprot.writeFieldBegin('relativeError', TType.DOUBLE, 1)
      oprot.writeDouble(self.relativeError)
      oprot.writeFieldEnd()
    if self.resetProbability is not None:
      oprot.writeFieldBegin('resetProbability', TType.DOUBLE, 2)
      oprot.writeDouble(self.resetProbability)
      oprot.writeFieldEnd()
    if self.minProbability is not None:
      oprot.writeFieldBegin('minProbability', TType.DOUBLE, 3)
      oprot.writeDouble(self.minProbability)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    if self.relativeError is None:
      raise TProtocol.TProtocolException(message='Required field relativeError is unset!')
    if self.resetProbability is None:
      raise TProtocol.TProtocolException(message='Required field resetProbability is unset!')
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.relativeError)
    value = (value * 31) ^ hash(self.resetProbability)
    value = (value * 31) ^ hash(self.minProbability)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class InvalidNodeIdException(TException):
  """
  Attributes:
   - message
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'message', None, None, ), # 1
  )

  def __init__(self, message=None,):
    self.message = message

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.message = iprot.readString()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('InvalidNodeIdException')
    if self.message is not None:
      oprot.writeFieldBegin('message', TType.STRING, 1)
      oprot.writeString(self.message)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __str__(self):
    return repr(self)

  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.message)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class InvalidIndexException(TException):
  """
  Attributes:
   - message
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'message', None, None, ), # 1
  )

  def __init__(self, message=None,):
    self.message = message

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.message = iprot.readString()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('InvalidIndexException')
    if self.message is not None:
      oprot.writeFieldBegin('message', TType.STRING, 1)
      oprot.writeString(self.message)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __str__(self):
    return repr(self)

  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.message)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class InvalidArgumentException(TException):
  """
  Attributes:
   - message
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'message', None, None, ), # 1
  )

  def __init__(self, message=None,):
    self.message = message

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.message = iprot.readString()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('InvalidArgumentException')
    if self.message is not None:
      oprot.writeFieldBegin('message', TType.STRING, 1)
      oprot.writeString(self.message)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __str__(self):
    return repr(self)

  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.message)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class UndefinedGraphException(TException):
  """
  Attributes:
   - message
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'message', None, None, ), # 1
  )

  def __init__(self, message=None,):
    self.message = message

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.message = iprot.readString()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('UndefinedGraphException')
    if self.message is not None:
      oprot.writeFieldBegin('message', TType.STRING, 1)
      oprot.writeString(self.message)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __str__(self):
    return repr(self)

  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.message)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class SQLException(TException):
  """
  Attributes:
   - message
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'message', None, None, ), # 1
  )

  def __init__(self, message=None,):
    self.message = message

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRING:
          self.message = iprot.readString()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('SQLException')
    if self.message is not None:
      oprot.writeFieldBegin('message', TType.STRING, 1)
      oprot.writeString(self.message)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __str__(self):
    return repr(self)

  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.message)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class UnequalListSizeException(TException):

  thrift_spec = (
  )

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('UnequalListSizeException')
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __str__(self):
    return repr(self)

  def __hash__(self):
    value = 17
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)
