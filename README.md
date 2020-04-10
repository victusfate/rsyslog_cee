
This is a translation of https://github.com/enobrev/rsyslog-cee to python, which is a fork of winston-rsyslog-cee, but it sends directly to syslog instead of using winston.

# Options

```python
    # import {Logger} from 'rsyslog-cee'; OR
    from rsyslog_cee import Logger

    oLogger = Logger(
        {
            service: 'Whatever', # The App Name for Syslog
            console: true,       # Output logs to console
            syslog:  true        # Output logs to syslog
        }
    );

    oTimer = oLogger.startTimer('Test');

    oLogger.d('Debug', {test: 'Debugging'});
    oLogger.w('Warn', {test: 'Warning'});
    oLogger.i('Info', {test: 'Information'});
    oLogger.n('Notice', {test: 'Notification'});
    oLogger.e('Error', {test: 'Error!'});
    oLogger.c('Critical', {test: 'Critical!'});
    oLogger.a('Alert', {test: 'Hey!'});
    oLogger.em('Emergency', {test: 'OMGWTF!!'});

    sleep 1
    oLogger.dt(oTimer)
    oLogger.removeSyslog()

```