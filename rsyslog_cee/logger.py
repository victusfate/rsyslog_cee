import sys
import json
import hashlib
import urllib
import syslog
import datetime
from .timer import Timer,TimeKeeper
import copy
import functools
import re
import logging

# logging.StreamHandler(sys.stdout)
# logging.basicConfig(level=logging.INFO)

from typing import Optional
from urllib.parse import urlparse

# import crypto           from 'crypto';
# import Syslogh          from 'syslogh';
# import util             from 'util';
# import url              from "url";


class LoggerOptions:
  service:        str
  purpose:        Optional[str]
  thread_hash:    Optional[str]
  parent_hash:    Optional[str]

  console:        Optional[bool]
  syslog:         Optional[bool]

  request:        None

  def __init__(self,service,purpose=None,thread_hash=None,parent_hash=None,console=None,syslog=None,request=None):
    self.service     = service
    self.purpose     = purpose
    self.thread_hash = thread_hash
    self.parent_hash = parent_hash
    self.console     = console
    self.syslog      = syslog
    self.request     = request


class TraceTags:
  thread_hash: Optional[str]
  parent_hash: Optional[str]


SYSLOG_TO_LOGGING_SEVERITY = {
    syslog.LOG_DEBUG   : logging.DEBUG,
    syslog.LOG_INFO    : logging.INFO,
    syslog.LOG_NOTICE  : logging.INFO,
    syslog.LOG_WARNING : logging.WARNING, 
    syslog.LOG_ERR     : logging.ERROR,
    syslog.LOG_CRIT    : logging.CRITICAL,
    syslog.LOG_ALERT   : logging.CRITICAL,
    syslog.LOG_EMERG   : logging.CRITICAL,
}


class Logger:
  service:         str
  request_hash:    str
  thread_hash:     str
  parent_hash:     Optional[str]
  start_timestamp: str

  index:           int
  metrics:         Timer
  is_error:        bool
  console:         bool
  syslog:          bool
  purpose:         Optional[str] = None

  Globals = {}        #  [index: string]: any
  tags    = {}        # [index: string]: any

  logger:         None
  handler:        None

  severity_strings = {}

  def __init__(self,oOptions: LoggerOptions):
    self.Globals    = {}
    self.index      = 0
    self.is_error   = False
    self.console    = False
    self.syslog     = False

    if not oOptions.service:
      raise Exception('Please set service name in options')

    self.service = oOptions.service

    self.logger = logging.getLogger(self.service)
    self.logger.handlers = []
    self.logger.setLevel(logging.DEBUG)
    self.handler = logging.StreamHandler(sys.stdout)
    self.handler.setLevel(logging.DEBUG)
    self.logger.addHandler(self.handler)
    self.logger.propagate = False

    # self.logger.debug('test debug')
    # self.logger.info('test info')
    # self.logger.warning('test warning')
    # self.logger.error('test error')
    # self.logger.critical('test critical')

    self.severity_strings[syslog.LOG_DEBUG]   = 'DEBUG'
    self.severity_strings[syslog.LOG_INFO]    = 'INFO'
    self.severity_strings[syslog.LOG_NOTICE]  = 'NOTICE'
    self.severity_strings[syslog.LOG_WARNING] = 'WARN'    
    self.severity_strings[syslog.LOG_ERR]     = 'ERROR'
    self.severity_strings[syslog.LOG_CRIT]    = 'CRITICAL'
    self.severity_strings[syslog.LOG_ALERT]   = 'ALERT'
    self.severity_strings[syslog.LOG_EMERG]   = 'EMERGENCY' 
   
    

    if oOptions.console:
      self.addConsole()

    if oOptions.syslog:
      self.addSyslog()

    self.request_hash = hashlib.sha1(str(TimeKeeper.getTime()).encode('utf-8')).hexdigest()[0:8]
    self.thread_hash  = self.request_hash
    self.parent_hash  = None

    if oOptions.request:
      if oOptions.request.headers and oOptions.request.headers['x-request-id']:
        self.thread_hash = str(oOptions.request.headers['x-request-id'])
      
      oUrl = urlparse(oOptions.request.url or '')

      if '--t' in oUrl.query:
        self.thread_hash = str(oUrl.query['--t'])

      if '--p' in oUrl.query:
        self.parent_hash = str(oUrl.query['--p'])

      self.addRequestContext(oOptions.request)
    else:
      if oOptions.thread_hash:
        self.thread_hash = oOptions.thread_hash

      if oOptions.parent_hash:
        self.parent_hash = oOptions.parent_hash

    self.metrics = Timer()
    self.metrics.start('_REQUEST')

    self.start_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if oOptions.purpose:
      self.setPurpose(oOptions.purpose)

  def addConsole(self):
    self.console = True

  def removeConsole(self):
    self.console = False

  def addSyslog(self):
    self.syslog = True;
    syslog.openlog(self.service, syslog.LOG_PID, syslog.LOG_LOCAL7)

  def removeSyslog(self):
    self.syslog = False
    syslog.closelog()

  def getTraceTags(self) -> TraceTags:
      return TraceTags(
          thread_hash=self.thread_hash,
          parent_hash=self.request_hash
      )

  def justAddContext(self,mContext):
    self._indexedLogRewriter('', mContext)

  # TODO find a format for oRequest that will work  here, maybe the requests module 
  # for now assume a Bottle request object TBD https://bottlepy.org/docs/dev/api.html#bottle.BaseRequest
  def addRequestContext(self,oRequest):
    self._indexedLogRewriter('', {
        '#request': {
            'headers':    json.dumps(oRequest.headers),
            'host':       oRequest.headers['host'],
            'method':     oRequest.method,
            'parameters': {
                'path':  None,
                'post':  None,
                'query': None,
            },
            'path':       None,
            'referrer':   oRequest.headers['referer'],
            'uri':        oRequest.url
        },
        '#user': {
            'agent': oRequest.headers['user-agent'],
            'ip':    oRequest.remote_addr
        }
    })

  def addTag(self,tag: str, value):
    if not self.tags:
      self.tags = {}
    self.tags[tag] = value

  def setProcessIsError(self,is_error: bool):
    self.is_error = is_error

  def setPurpose(self,purpose: str):
    self.purpose = purpose

  @staticmethod
  def _objectFromPath(oObject, sPath: str, mValue):
    # TODO convert from js to python -> not sure what this is doing
    # return sPath.split('.').reduce(
    #   (oValue: {[index: string]: any}, sKey: string, iIndex: number, aSplit: any) => 
    #     oValue[sKey] = iIndex === aSplit.length - 1 ? mValue : {}, oObject);

    aPath = sPath.split('.')
    for iIndex in range(len(aPath)):
      sKey = aPath[iIndex]
      if iIndex == len(aPath) - 1:
        oObject[sKey] = mValue
    return oObject
    

  @staticmethod
  def _syslogFormatter(oMessage) -> str:
    oMessageOut = {}
    for sKey,mValue in oMessage.items():
      try:
        data = mValue.decode('base64')
        oMessageOut[sKey] = data
      except (UnicodeDecodeError, AttributeError):
        oMessageOut[sKey] = mValue

    return json.dumps(oMessageOut)

  def _indexedLogRewriter(self,sMessage: str, oMeta=None):

    oClone = copy.copy(oMeta) if oMeta else {}

    oOutput = {
      '--action': sMessage
    }

    if oClone:
      if 'action'in oClone:
        oOutput['--action'] = oClone['action']
        del oClone['action']

      self.index += 1

      oOutput['--i'] = self.index
      oOutput['--r'] = self.request_hash
      oOutput['--t'] = self.thread_hash

      if self.parent_hash:
        oOutput['--p'] = self.parent_hash

      # Move all "--*" items to root
      
      for sKey in oMeta.keys():
        try:
          if sKey.index('--') == 0:
            oOutput[sKey] = oClone[sKey]
            del oClone[sKey]

          if sKey.index('#') == 0:
            sStrippedKey = re.sub('^#+','',sKey)
            oClone[sStrippedKey] = oClone[sKey]
            del oClone[sKey]

            if ['str', 'float', 'bool'].find(type(oClone[sStrippedKey])) > -1:
              self.Globals[sStrippedKey] = oClone[sStrippedKey]
            else:
              oTemp = copy.copy(self.Globals[sStrippedKey])
              oTemp.update(oClone[sStrippedKey])
              self.Globals[sStrippedKey] = oTemp
        except:
          pass

      if len(oClone) > 0:
        Logger._objectFromPath(oOutput, oOutput['--action'], oClone)

    return oOutput

  def setLevel(self,iSeverity):
    self.logger = logging.getLogger(self.service)
    self.logger.handlers = []
    self.logger.setLevel(iSeverity)
    self.handler = logging.StreamHandler(sys.stdout)
    self.handler.setLevel(iSeverity)
    self.logger.addHandler(self.handler)
    self.logger.propagate = False
    # self.logger.debug('test debug')
    # self.logger.info('test info')
    # self.logger.warning('test warning')
    # self.logger.error('test error')
    # self.logger.critical('test critical')

  def log(self,iSeverity: int, sAction: str, oMeta):
    # print('logger.log iSeverity',iSeverity,'sAction',sAction,'oMeta',oMeta,'self.console',self.console)
    oParsed  = Logger.JSONifyErrors(oMeta)
    oMessage = self._indexedLogRewriter(sAction,oParsed)
    sMessage = Logger._syslogFormatter(oMessage)

    if self.syslog:
      syslog.syslog(iSeverity, sMessage);

    if self.console:
      oMessage['--sn'] = self.severity_strings[iSeverity]
      sMessage = json.dumps(oMessage,sort_keys=True,separators=(',', ': '))
      iLoggingSeverity = SYSLOG_TO_LOGGING_SEVERITY[iSeverity]
      self.logger.log(iLoggingSeverity,sMessage)

  # 
  # @param sOverrideName
  # @returns {{"--ms": *, "--i": number, "--summary": boolean, "--span": {_format: string, version: number, start_timestamp: string, end_timestamp: string, service: string, indicator: boolean, metrics: string, error: boolean, name: string, tags: {}, context: {}}}}
  # 
  def summary(self,sOverrideName: str = 'Summary'):
    self.index += 1
    iTimer = self.metrics.stop('_REQUEST')
    oSummary = {
        '--ms':          iTimer,
        '--i':           self.index,
        '--summary':     True,
        '--span': {
            '_format':         'SSFSpan.DashedTrace',
            'version':         1,
            'start_timestamp': self.start_timestamp,
            'end_timestamp':   datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'service':         self.service,
            'metrics':         json.dumps(self.metrics.getAll()),
            'error':           self.is_error,
            'name':            self.purpose,
            'tags':            self.tags,
            'context':         self.Globals
        }
    }

    self.log(syslog.LOG_INFO, '.'.join([self.service, sOverrideName]), oSummary)
    return oSummary

  # 
  # 
  # @param {object} oMeta
  # @return {string}
  #

  @staticmethod
  def JSONifyErrors(oMeta):
    # if oMeta:
    #   bFoundErrors = False

    #   TODO start here
    #   maybe look https://docs.python.org/3/library/traceback.html
    #   original error checker https://github.com/enobrev/rsyslog-cee/blob/master/src/Logger.ts#L301-L331

    #   if bFoundErrors and sMeta:
    #     return JSON.parse(sMeta)

    return oMeta

  def d(self,sAction: str, oMeta):
    self.log(syslog.LOG_DEBUG, sAction, oMeta)

  def i(self,sAction: str, oMeta):
    self.log(syslog.LOG_INFO, sAction, oMeta);
  
  def n(self,sAction: str, oMeta):
    self.log(syslog.LOG_NOTICE, sAction, oMeta)

  def w(self,sAction: str, oMeta):
    self.log(syslog.LOG_WARNING, sAction, oMeta)

  def e(self,sAction: str, oMeta):
    self.log(syslog.LOG_ERR, sAction, oMeta)

  def c(self,sAction: str, oMeta):
    self.log(syslog.LOG_CRIT, sAction, oMeta)

  def a(self,sAction: str, oMeta):
    self.log(syslog.LOG_ALERT, sAction, oMeta)

  def em(self,sAction: str, oMeta):
    self.log(syslog.LOG_EMERG, sAction, oMeta)

  def dt(self,oTime: TimeKeeper, sActionOverride: Optional[str] = None):
    self.d(sActionOverride if sActionOverride else oTime.label(), {'--ms': oTime.stop()})
  
  def startTimer(self,sLabel: str) -> TimeKeeper:
    return self.metrics.start(sLabel)

  def stopTimer(self,sLabel: str) -> float:
    return self.metrics.stop(sLabel)
