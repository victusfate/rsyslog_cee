import hashlib
import urllib
import syslogh
import timer
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

  request:        Optional[request]

  def __init__(self,service,purpose=None,thread_hash=None,parent_hash=None,console=None,syslog=None,request=None):
    self.service     = service
    self.purpose     = purpose
    self.thread_hash = thread_hash
    self.parent_hash = parent_hash
    self.console     = console
    self.syslog      = syslog
    self.request     = request


class TraceTags:
  '--t': Optional[str]
  '--p': Optional[str]



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
  purpose:         Optional[str]

  Globals = {}        #  [index: string]: any
  tags: Optional[{}]  # [index: string]: any

  def __init__(self,oOptions: LoggerOptions):
    self.Globals    = {}
    self.index      = 0
    self.is_error   = False
    self.console    = False
    self.syslog     = False

    if not oOptions.service:
      raise Exception('Please set service name in options')

    self.service = oOptions.service

    if oOptions.console:
      self.addConsole()

    if oOptions.syslog:
      self.addSyslog()

    self.request_hash = hashlib.sha1('' + TimeKeeper.getTime()).hexdigest()[0:8];
    self.thread_hash  = self.request_hash

    if oOptions.request:
      if oOptions.request.headers and oOptions.request.headers['x-request-id']:
        self.thread_hash = str(oOptions.request.headers['x-request-id'])
      
      oUrl = urlparse(oOptions.request.url or '')

      if oUrl.query['--t']:
        self.thread_hash = str(oUrl.query['--t'])

      if (oUrl.query['--p']) {
          self.parent_hash = <string> oUrl.query['--p'];
      }

      self.addRequestContext(oOptions.request);
    } else {
        if (oOptions.thread_hash) {
            self.thread_hash = oOptions.thread_hash;
        }

        if (oOptions.parent_hash) {
            self.parent_hash = oOptions.parent_hash;
        }
    }

    self.metrics = new Timer();
    self.metrics.start('_REQUEST');

    self.start_timestamp = new Date().toISOString();

    if (oOptions.purpose) {
        self.setPurpose(oOptions.purpose);
    }

  addConsole() {
      self.console = true;
  }

  removeConsole() {
      self.console = false;
  }

  addSyslog() {
      self.syslog = true;
      Syslogh.openlog(self.service, Syslogh.PID, Syslogh.LOCAL7)
  }

  removeSyslog() {
      self.syslog = false;
      Syslogh.closelog();
  }

  getTraceTags(): TraceTags {
      return {
          '--t': self.thread_hash,
          '--p': self.request_hash
      };
  }

  justAddContext(mContext: any) {
      self._indexedLogRewriter('', mContext);
  }

  addRequestContext(oRequest: http.IncomingMessage) {
      self._indexedLogRewriter('', {
          '#request': {
              headers:    JSON.stringify(oRequest.headers),
              host:       oRequest.headers.host,
              method:     oRequest.method,
              parameters: {
                  path:  null,
                  post:  null,
                  query: null
              },
              path:       null,
              referrer:   oRequest.headers.referer,
              uri:        oRequest.url
          },
          '#user': {
              agent: oRequest.headers['user-agent'],
              ip:    oRequest.connection.remoteAddress
          }
      });
  }

  addTag(tag: string, value: any) {
      if (!self.tags) {
          self.tags = {};
      }

      self.tags[tag] = value;
  }

  setProcessIsError(is_error: boolean) {
      self.is_error = is_error;
  }

  setPurpose(purpose: string) {
      self.purpose = purpose;
  }

  static _objectFromPath (oObject: any, sPath: string, mValue: any) {
      sPath.split('.').reduce((oValue: {[index: string]: any}, sKey: string, iIndex: number, aSplit: any) => oValue[sKey] = iIndex === aSplit.length - 1 ? mValue : {}, oObject);
  };

  static _syslogFormatter (oMessage: any): string {
      return '@cee: ' + JSON.stringify(oMessage, (sKey, mValue) => {
          return mValue instanceof Buffer
              ? mValue.toString('base64')
              : mValue;
      });
  };

  _indexedLogRewriter = (sMessage: string, oMeta?: any) => {
      let oClone = oMeta ? Object.assign({}, oMeta) : {};

      let oOutput: any = {
          '--action': sMessage
      };

      if (oClone) {
          if (oClone.action) {
              oOutput['--action'] = oClone.action;
              delete oClone.action;
          }

          self.index++;

          oOutput['--i'] = self.index;
          oOutput['--r'] = self.request_hash;
          oOutput['--t'] = self.thread_hash;

          if (self.parent_hash) {
              oOutput['--p'] = self.parent_hash;
          }

          // Move all "--*" items to root
          Object.keys(oClone).map(sKey => {
              if (sKey.indexOf('--') === 0) {
                  oOutput[sKey] = oClone[sKey];
                  delete oClone[sKey];
              }

              if (sKey.indexOf('#') === 0) {
                  const sStrippedKey = sKey.replace(/^#+/, '');
                  oClone[sStrippedKey] = oClone[sKey];
                  delete oClone[sKey];

                  if (['string', 'number', 'boolean'].indexOf(typeof oClone[sStrippedKey]) > -1) {
                      self.Globals[sStrippedKey] = oClone[sStrippedKey];
                  } else {
                      self.Globals[sStrippedKey] = Object.assign({}, self.Globals[sStrippedKey], oClone[sStrippedKey]);
                  }
              }
          });

          if (Object.keys(oClone).length > 0) {
              Logger._objectFromPath(oOutput, oOutput['--action'], oClone);
          }
      }

      return oOutput;
  };

  private log(iSeverity: number, sAction: string, oMeta?: any) {
      const oParsed  = Logger.JSONifyErrors(oMeta);
      const oMessage = self._indexedLogRewriter(sAction, oParsed);
      const sMessage = Logger._syslogFormatter(oMessage);

      if (self.syslog) {
          Syslogh.syslog(iSeverity, sMessage);
      }

      if (self.console) {
          const sMessage = JSON.stringify(oMessage, null, '   ');
          switch (iSeverity) {
              case Syslogh.DEBUG:   console.debug('DEBUG',   sMessage); break;
              case Syslogh.INFO:    console.info( 'INFO',    sMessage); break;
              case Syslogh.NOTICE:  console.log(  'NOTICE',  sMessage); break;
              case Syslogh.WARNING: console.warn( 'WARNING', sMessage); break;
              case Syslogh.ERR:     console.error('ERR',     sMessage); break;
              case Syslogh.CRIT:    console.error('CRIT',    sMessage); break;
              case Syslogh.ALERT:   console.error('ALERT',   sMessage); break;
              case Syslogh.EMERG:   console.error('EMERG',   sMessage); break;
          }
      }
  }

  /**
    *
    * @param sOverrideName
    * @returns {{"--ms": *, "--i": number, "--summary": boolean, "--span": {_format: string, version: number, start_timestamp: string, end_timestamp: string, service: string, indicator: boolean, metrics: string, error: boolean, name: string, tags: {}, context: {}}}}
    */
  summary(sOverrideName: string = 'Summary') {
      self.index++;
      const iTimer = self.metrics.stop('_REQUEST');
      const oSummary = {
          '--ms':          iTimer,
          '--i':           self.index,
          '--summary':     true,
          '--span': {
              _format:         'SSFSpan.DashedTrace',
              version:         1,
              start_timestamp: self.start_timestamp,
              end_timestamp:   new Date().toISOString(),
              service:         self.service,
              metrics:         JSON.stringify(self.metrics.getAll()),
              error:           self.is_error,
              name:            self.purpose,
              tags:            self.tags,
              context:         self.Globals
          }
      };

      self.log(Syslogh.INFO, [self.service, sOverrideName].join('.'), oSummary);

      return oSummary;
  }

  /**
    *
    * @param {object} oMeta
    * @return {string}
    */
  static JSONifyErrors(oMeta: object) {
      if (oMeta) {
          let bFoundErrors = false;

          // https://stackoverflow.com/a/18391400/14651
          const sMeta = JSON.stringify(oMeta, (sKey: string , mValue: any) => {
              if (util.types && util.types.isNativeError ? util.types.isNativeError(mValue) : util.isError(mValue)) {
                  bFoundErrors = true;
                  let oError: {[index: string]: any} = {};

                  Object.getOwnPropertyNames(mValue).forEach(sKey => {
                      if (sKey === 'stack') {
                          oError[sKey] = mValue[sKey].split('\n');
                      } else {
                          oError[sKey] = mValue[sKey];
                      }
                  });

                  return oError;
              }

              return mValue;
          });

          if (bFoundErrors && sMeta) {
              return JSON.parse(sMeta);
          }
      }

      return oMeta;
  }

  d(sAction: string, oMeta?: any) {
      self.log(Syslogh.DEBUG, sAction, oMeta);
  }

  i(sAction: string, oMeta?: any) {
      self.log(Syslogh.INFO, sAction, oMeta);
  }

  n(sAction: string, oMeta?: any) {
      self.log(Syslogh.NOTICE, sAction, oMeta);
  }

  w(sAction: string, oMeta?: any) {
      self.log(Syslogh.WARNING, sAction, oMeta);
  }

  e(sAction: string, oMeta?: any) {
      self.log(Syslogh.ERR, sAction, oMeta);
  }

  c(sAction: string, oMeta?: any) {
      self.log(Syslogh.CRIT, sAction, oMeta);
  }

  a(sAction: string, oMeta?: any) {
      self.log(Syslogh.ALERT, sAction, oMeta);
  }

  em(sAction: string, oMeta?: any) {
      self.log(Syslogh.EMERG, sAction, oMeta);
  }

  dt(oTime: TimeKeeper, sActionOverride?: string) {
      self.d(sActionOverride ? sActionOverride : oTime.label(), {'--ms': oTime.stop()});
  }
  
  startTimer(sLabel: string): TimeKeeper {
      return self.metrics.start(sLabel);
  }

  stopTimer(sLabel: string): number {
      return self.metrics.stop(sLabel);
  }
