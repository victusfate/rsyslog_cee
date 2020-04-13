
import time
import rsyslog_cee
from rsyslog_cee.logger import Logger,LoggerOptions

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
