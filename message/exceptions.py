import logging

class TaskException(Exception):

    def __init__(self, message, logger=None, *args, **kwargs):
        if logger:
            self._logger = logger
            self.log_exception(message)
        else:
            self._logger = logging.getLogger('django_c2dm')
            self._logger.debug(message)
        super(Exception, self).__init__(message)

    def log_exception(self, message):
        self._logger.error(message)


class InvalidRegistrationException(TaskException):

    def log_exception(self, message):
        self._logger.info(message)


class NotRegisteredException(TaskException):

    def log_exception(self, message):
        self._logger.info(message)


class QuotaExceededException(TaskException): pass


class DeviceQuotaExceededException(TaskException): pass


class MessageTooBigException(TaskException): pass


class MissingCollapseKeyException(TaskException): pass


class UnknownErrorCodeException(TaskException): pass


class UrlErrorCodeException(TaskException): pass


class UrlErrorException(TaskException): pass


class ErrorInvalidAuthTokenException(TaskException): pass


class InvalidResponseException(TaskException): pass


class UnknownHttpErrorCodeException(TaskException): pass
