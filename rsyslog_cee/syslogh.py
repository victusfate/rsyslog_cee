from enum import Enum

#
# Option flags for openlog.
# 
# LOG_ODELAY no longer does anything.
# LOG_NDELAY is the inverse of what it used to be.
# 
class Option(Enum):
    PID     =  1 << 0  # log the pid with each message
    CONS    =  2 << 0, # log on the console if errors in sending
    ODELAY  =  4 << 0, # delay open until first syslog() (default)
    NDELAY  =  8 << 0, # don't delay open
    NOWAIT  = 10 << 0, # don't wait for console forks: DEPRECATED
    PERROR  = 20 << 0  # log to stderr as well

class Options:
    flags: Option

class Facility(Enum):
    KERN	    = 0  << 3   # kernel messages
    USER	    = 1  << 3   # random user-level messages
    MAIL	    = 2  << 3   # mail system
    DAEMON	  = 3  << 3   # system daemons
    AUTH	    = 4  << 3   # security/authorization messages
    SYSLOG	  = 5  << 3   # messages generated internally by syslogd
    LPR		    = 6  << 3   # line printer subsystem
    NEWS	    = 7  << 3   # network news subsystem
    UUCP	    = 8  << 3   # UUCP subsystem
    CRON	    = 9  << 3   # clock daemon
    AUTHPRIV	= 10 << 3   # security/authorization messages (private)


    # other codes through 15 reserved for system use
    LOCAL0	    = 16 << 3  # reserved for local use
    LOCAL1	    = 17 << 3  # reserved for local use
    LOCAL2	    = 18 << 3  # reserved for local use
    LOCAL3	    = 19 << 3  # reserved for local use
    LOCAL4	    = 20 << 3  # reserved for local use
    LOCAL5	    = 21 << 3  # reserved for local use
    LOCAL6	    = 22 << 3  # reserved for local use
    LOCAL7	    = 23 << 3	 # reserved for local use


class Priority(Enum):
    EMERG	  = 0     # system is unusable
    ALERT	  = 1     # action must be taken immediately
    CRIT	  = 2     # critical conditions
    ERR		  = 3     # error conditions
    WARNING	= 4 	  # warning conditions
    NOTICE	= 5 	  # normal but significant condition 
    INFO	  = 6	    # informational
    DEBUG	  = 7 	  # debug-level messages


class Syslogh:

  # Options (flags)
  PID:     int
  CONS:    int
  ODELAY:  int
  NDELAY:  int
  NOWAIT:  int
  PERROR:  int

  # facilities
  KERN:    int
  USER:    int
  MAIL:    int
  DAEMON:  int
  AUTH:    int
  SYSLOG:  int
  LPR:     int
  NEWS:    int
  UUCP:    int
  CRON:    int  

  LOCAL0:  int
  LOCAL1:  int
  LOCAL2:  int
  LOCAL3:  int
  LOCAL4:  int
  LOCAL5:  int
  LOCAL6:  int
  LOCAL7:  int

  # severities
  EMERG:   int
  ALERT:   int
  CRIT:    int
  ERR:     int
  WARNING: int
  NOTICE:  int
  INFO:    int
  DEBUG:   int

  def openlog(self,identity: str, flags: Options, facility: Facility):
    return

  def syslog(self,priority: Priority, message: str):
    return

  def closelog(self):
    return
