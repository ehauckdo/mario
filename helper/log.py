import os
import logging
import logging.handlers

# use this to set a size limit for the log file
# Author: logc
# Source: https://stackoverflow.com/questions/24157278/limit-python-log-file
class TruncatedFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, encoding=None, delay=0):
        super(TruncatedFileHandler, self).__init__(
            filename, mode, maxBytes, 0, encoding, delay)

    def doRollover(self):
        """Truncate the file"""
        if self.stream:
            self.stream.close()
        dfn = self.baseFilename + ".1"
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.baseFilename, dfn)
        os.remove(dfn)
        self.mode = 'w'
        self.stream = self._open()
