from django_c2dm.message.exceptions import *


class MessageRequest(object):
    'Request interface'

    def __init__(self):
        self._logger = None

    def check_data(self):
        pass

    def set_logger(self, logger):
        self._logger = logger

    def get_collapse_key(self):
        raise NotImplementedError('get_collapse_key')

    def get_registration_id(self):
        raise NotImplementedError('get_registration_id')

    def get_delay_while_idle(self):
        'Return boolean'
        raise NotImplementedError('get_delay_while_idle')

    def get_data(self):
        'Return dictionary key_name => data'
        raise NotImplementedError('get_data')


class MessageResponse(object):
    'Response interface'

    def __init__(self):
        self._logger = None
        self._request = None
        self._error_data = ''
        # _task_id
        # None - if no task started
        # True/False - if task finished(positive/negative)
        # integer - task id
        self._task_id = None

    def set_task_id(self, id):
        self._task_id = id

    def get_task_id(self):
        return self._task_id

    def set_request(self, request):
        self._request = request

    def set_logger(self, logger):
        self._logger = logger

    def set_error(self, error_name, error_data=''):
        '''
        Known errors(name error / description ):
            invalid_registration - 
            not_registered -
            quota_exceeded - 
            device_quota_exceeded - 
            message_too_big -
            missing_collapse_key -
            unknown_error_code - 
            url_error -
        '''
        self._error_name = error_name
        self._error_data = error_data
        try:
            self.__getattribute__('error_%s' % error_name)()
        except AttributeError:
            self.error_not_implemented()
        self.set_task_id(False)

    def set_result(self, id):
        '''
        id - id from response c2dm server
        '''
        self._id = id
        MessageResponse.set_task_id(self, True)

    def get_result(self):
        return self._id

    def get_error_name(self):
        return self._error_name

    def get_error_data(self):
        if self._error_data:
            return self._error_data
        else:
            return 'RegID [%s], CollapseKey [%s], Data [%s]' % \
                    (self._request.get_registration_id(),
                     self._request.get_collapse_key(),
                     self._request.get_data(),)

    def error_invalid_registration(self):
        raise InvalidRegistrationException(self.get_error_data(), self._logger)

    def error_not_registered(self):
        raise NotRegisteredException(self.get_error_data(), self._logger)

    def error_quota_exceeded(self):
        raise QuotaExceededException(self.get_error_data(), self._logger)

    def error_device_quota_exceeded(self):
        raise DeviceQuotaExceededException(self.get_error_data(), self._logger)

    def error_message_too_big(self):
        raise MessageTooBigException(self.get_error_data(), self._logger)

    def error_missing_collapse_key(self):
        raise MissingCollapseKeyException(self.get_error_data(), self._logger)

    def error_unknown_error_code(self):
        raise UnknownErrorCodeException(self.get_error_data(), self._logger)

    def error_url_error(self):
        raise UrlErrorException(self.get_error_data(), self._logger)

    def error_invalid_auth_token(self):
        raise ErrorInvalidAuthTokenException(self.get_error_data(), self._logger)

    def error_invalid_response(self):
        raise InvalidResponseException(self.get_error_data(), self._logger)

    def error_mismatch_sender_id(self):
        raise MismatchSenderId(self.get_error_data(), self._logger)

    def error_not_implemented(self):
        raise NotImplementedError('%s [%s]' % (self.get_error_name(), self.get_error_data()))
