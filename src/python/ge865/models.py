import logging

logger = logging.getLogger(__name__)

from commands import at

class _dumbLink(object):
  def process(self, command):
    command.parse('')
    return command

class Device(object):
  """A device contains manufacturer, serial info, etc...

  It's a safe base class for any high level feature set.  Obtaining
  information about a device is always a safe set of operations, and a
  particularly easy one to group.

  TODO: make testable
  """
  __cache__ = { }
  __features__ = { }
  link = None
  __attrs__ = { 'manufacturer': at.GMI,
                'model': at.GMM,
                'serial': at.GSN,
                'capabilities': at.GCAP,
                'revision': at.GMR, }
  def __init__(self, link):
    self.link = link
    self.__fetch__()

  def __repr__(self):
    # Only show instantiated attributes.
    l = ['### %r' % self.__class__ ]
    for k, v in self.__cache__.iteritems():
      l.append(' -- %20s %50s' % (k, v))
    return '\n'.join(l)

  def __fetch__(self):
    d = { }
    for k, v in self.__attrs__.iteritems():
      d[k] = getattr(self, k)
    return d
    
  def __getattr__(self, name):
    if name in self.__attrs__:
      data = self.__cache__.get(name,
               self.link.process(self.__attrs__[name]( )).getData( ))
      if name not in self.__cache__:
        self.__cache__[name] = data
      return data
    raise AttributeError("%s has no attribute: %s" % (self, name))
   
  def manufacturer(self):
    r = self.__cache__.get( 'manufacturer',
        self.link.process(at.GMI()).getData())
    if 'manufacturer' not in self.__cache__:
      self.__cache__['manufacturer'] = r
    return r

  def inspect(self, Feature):
    feature = Feature( )
    self.__features__[feature.__class__.__name__] = feature
    feature.setDevice(self)
    return feature

# class DeviceData


class Feature(object):
  device = None
  name   = 'Feature'
  def setDevice(self, device):
    self.device = device
  def getDevice(self):
    return self.device


class EnablerDisabler(Feature):
  name = 'EnableDisableControl'
  def __init__(self):
    pass
  __query__ = at.WellDefinedCommand
  __enabled__ = False
  def query(self):
    q = self.device.link.process(self.__query__.query( ))
    self.__enabled__ = q.getDevice( ) == 1
  def isEnabled(self):
    return self.__enabled__
  def enable(self):
    q = self.device.link.process(self.__query__.assign(1))
    if q.isOK( ):
      self.__enabled__ = True
  def disable(self):
    q = self.device.link.process(self.__query__.assign(0))
    if q.isOK( ):
      self.__enabled__ = True
    
class ElementList(Feature):
  name = "ElementListControl"

class Socket(Device):
  pass

class SIM(Device):
  """
  QSS
  CSIM pg 380
    read/write to SIM

  """
  pass

class TCPATRUN(object):
  """
    TCPATRUN
    TCPATRUNCFG
    SMSATWL

    pg 381
  """
class EvMoni(object):
  """
  """

class SMSATRUN(object):
  """
    pg 380
    enable/disable
    list of context configs
    whitelist
    SMSATRUN
     mode = 1/0 enables[default]/disable the service
     Eval incoming SMS as AT.

    SMSATRUNCFG
      instance - "AT instance" used range 2-3, default 3
      urcmode  - 0/1 disable/enable[default] feature
      timeout  - in minutes.  module reboots if timeout expires before
                 commands finish.  default 5. 1..60
      AT instance refers to :mod:`EvMoni` service.
      See ENAEVMONICFG
      
    SMSATWL
      How SMSATRUN messages are processed are controlled by the SMS whitelist.
      The list contains a list of elements representing either passwords or
      phone number.  There can be a max of 2 numbers, with a total of 8
      elements total, numbered 1 - 8.

      An incoming text must have a special PDU format containing the password
      in the PDU header, or the sender number must match a number on the
      whitelist.

      The query syntax returns a list of (entryType, string) tuples.

      * action - 0..2
        0 - Add an element
        1 - Delete an element
        2 - Print an element
      * index - 1..8
      * entryType - 0 - Phone number, 1 - password
        [max of two password types]
      * string - either a phone number or a password

    The feature is divided into two modes, Simple and Digest
    Incoming text beginning with "AT" or "HAT" is evaled.


    Simple
    ~~~~~~
    Originating SMS address matches a number in the whitelist
    SMS coding alphabet may be 7 bit or 8 bit

    Digest
    ~~~~~~
    The SMS User Data segment must contain a header containing the MD5 digest
    of the message text using a password matching a password element in the
    whitelist.
    SMS coding alphabet must be 8 bit
    
    +--------+------+----------+--------------------+
    | Offset | Size |    Value | Description        |
    +========+======+==========+====================+
    |      0 |    3 | 0xD0D0D0 | RunAT SMS Code     |
    +--------+------+----------+--------------------+
    |      3 |    1 |        0 | Transaction ID     |
    +--------+------+----------+--------------------+
    |      4 |    1 |     0x11 | Segment 1 of 1     |
    +--------+------+----------+--------------------+
    |      5 |    1 |          | Session ID         |
    +--------+------+----------+--------------------+
    |      6 |   24 |          | Digest: B64(MD5(   |
    |        |      |          | B64(MD5(PWD)):     |
    |        |      |          | B64(MD5(MSG))))    |
    +--------+------+----------+--------------------+
    |     30 |      |          | Useful Text        |
    +--------+------+----------+--------------------+

    pg 378
  """

class PDP(object):
  def __init__(self, link, ):
    pass

if __name__ == '__main__':
  import doctest
  doctest.testmod()

#####
# EOF