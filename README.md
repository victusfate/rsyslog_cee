
This is a translation of https://github.com/enobrev/rsyslog-cee to python, which is a fork of winston-rsyslog-cee, but it sends directly to syslog instead of using winston.

todo review if similar focused source https://github.com/blue-yonder/cee_syslog_handler

# Options

```python
import time
import rsyslog_cee
from rsyslog_cee import Logger,LoggerOptions

oLogger = Logger(
    LoggerOptions(
        service='Whatever', # The App Name for Syslog
        console= True,       # Output logs to console
        syslog=  True        # Output logs to syslog
    )
)

oTimer = oLogger.startTimer('Test')

oLogger.d('Debug', {'test': 'Debugging'})
oLogger.w('Warn', {'test': 'Warning'})
oLogger.i('Info', {'test': 'Information'})
oLogger.n('Notice', {'test': 'Notification'})
oLogger.e('Error', {'test': 'Error!'})
oLogger.c('Critical', {'test': 'Critical!'})
oLogger.a('Alert', {'test': 'Hey!'})
oLogger.em('Emergency', {'test': 'OMGWTF!!'})

time.sleep(1)

oLogger.dt(oTimer)
oLogger.removeSyslog()

```