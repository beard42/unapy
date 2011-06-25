import logging

logger = logging.getLogger(__name__)
class Loggable(object):
  def __init__(self):
    self.getLog( )
  def getLog(self):
    name     = self.__class__.__name__
    logger   = '.'.join([ __name__, name ])
    self.log = logging.getLogger(logger)


#####
# EOF
