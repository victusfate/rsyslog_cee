    from rsyslog_cee import Logger

    oLogger = Logger(
        {
            service: 'Whatever', # The App Name for Syslog
            console: True,       # Output logs to console
            syslog:  True        # Output logs to syslog
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

    sleep(1)
    
    oLogger.dt(oTimer)
    oLogger.removeSyslog()
