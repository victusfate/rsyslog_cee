import syslog
import time
import os
import psutil
import json
import inspect
from inspect import getframeinfo, stack

import absl.logging
absl.logging.set_verbosity('info')
absl.logging.set_stderrthreshold('info')

import rsyslog_cee
from rsyslog_cee.logger import Logger,LoggerOptions

oLogger = None
service_name = 'log'

def reset():
  global oLogger 
  oLogger = Logger(
      LoggerOptions(
          service=service_name, # The App Name for Syslog
          console= False,       # we log to console here
          syslog=  True         # Output logs to syslog
      )
  )

def set_log_service_name(new_name):
  global service_name
  service_name = new_name  

def set_logger(oNewLogger):
  global oLogger
  oLogger = oNewLogger

def __get_proc_info():
  caller = getframeinfo(inspect.stack()[3][0])
  file = os.path.basename(caller.filename)
  pid = os.getpid()
  process = psutil.Process(pid)
  memory_bytes = process.memory_info().rss  # in bytes
  action = os.path.splitext(file)[0] + '.' + inspect.stack()[3].function
  return { 'action': action, 'file': file, 'line_number': caller.lineno, 'pid': pid, 'memory_bytes': memory_bytes, 'timestamp': int(time.time())  }


def __proc_info_to_line_string(ld):
  return "%d %d %d %s %d" % (ld['pid'],ld['memory_bytes'],ld['timestamp'],ld['file'], ld['line_number'])


def __log_level(level,*argv):
  ld = __get_proc_info()
  # line_string = __proc_info_to_line_string(ld)
  # print(line_string,*argv)
  output_message = []
  for arg in argv:
    output_message.append('{}')
  output_format = ' '.join(output_message)
  output_string = output_format.format(*argv)
  oLogger.log(level,ld['action'],{ 'proc_info': ld, 'message' : output_string })
  ld['message'] = output_string
  print(json.dumps(ld))

def debug(*argv):
  return __log_level(syslog.LOG_DEBUG,*argv)

def info(*argv):
  return __log_level(syslog.LOG_INFO,*argv)

def err(*argv):
  return __log_level(syslog.LOG_ERR,*argv)

def alert(*argv):
  return __log_level(syslog.LOG_ALERT,*argv)
