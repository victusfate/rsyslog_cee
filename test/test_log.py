
import time
import rsyslog_cee
from rsyslog_cee.logger import Logger,LoggerOptions
from rsyslog_cee import log

import logging

def test_log():
  oNewLogger = Logger(
      LoggerOptions(
          service='Whatever.log', # The App Name for Syslog
          console= True,          # we log to console here
          syslog=  False          # Output logs to syslog
      )
  )
  log.set_logger(oNewLogger)

  # see logging.basicConfig(level=logging.INFO)
  log.oLogger.setLevel(logging.DEBUG)
  log.debug('test debug -> this shows now')
  log.oLogger.setLevel(logging.INFO)
  log.debug('test debug -> this will not show due to min log level info')
  log.info('test info')
  log.warning('test warning')
  log.err('test err')
  log.alert('test alert')
  log.oLogger.summary()

test_log()

def test_logger():
  oLogger = Logger(
      LoggerOptions(
          service='Whatever.oLogger', # The App Name for Syslog
          console= True,              # Output logs to console
          syslog=  False              # Output logs to syslog
      )
  )

  oTimer = oLogger.startTimer('Test')

  oLogger.setLevel(logging.DEBUG)
  oLogger.d('Debug', {'test': 'Debugging, this shows now'})
  oLogger.setLevel(logging.INFO)
  oLogger.d('Debug', {'test': 'Debugging, this will not show due to min log level info'})
  oLogger.w('Warn', {'test': 'Warning'})
  oLogger.i('Info', {'test': 'Information'})
  oLogger.n('Notice', {'test': 'Notification'})
  oLogger.e('Error', {'test': 'Error!'})
  oLogger.c('Critical', {'test': 'Critical!'})
  oLogger.a('Alert', {'test': 'Hey!'})
  oLogger.em('Emergency', {'test': 'OMGWTF!!'})

  time.sleep(1)

  oLogger.dt(oTimer)

  oLogger.summary()
  oLogger.removeSyslog()

test_logger()



