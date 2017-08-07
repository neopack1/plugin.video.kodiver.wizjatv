import xbmc


class ContextAwareLogger:

    context = None

    def __init__(self, context):
        self.context = context

    def log_notice(self, message):
        self._log(message, xbmc.LOGNOTICE)

    def log_warn(self, message):
        self._log(message, xbmc.LOGWARNING)

    def log_err(self, message):
        self._log(message, xbmc.LOGERROR)

    def _log(self, message, level):
        xbmc.log('{0}: {1}'.format(self.context, message), level)
