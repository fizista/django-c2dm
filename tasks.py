import hashlib
import urllib, urllib2
from urllib2 import URLError

from celery.exceptions import SoftTimeLimitExceeded
from celery.decorators import task

from django_c2dm.models import DeviceChannelInfo
from django_c2dm import settings


C2DM_URL = 'https://android.apis.google.com/c2dm/send'


class TaskException(Exception):

    def __init__(self, message, logger=None, *args, **kwargs):
        if logger:
            self._logger = logger
            self.log_exception(message)
        super(Exception, self).__init__(message)

    def log_exception(self, message):
        self._logger.error(message)


class AndroidDeviceNotRegisteredException(TaskException):
    '''
    When the device is not registered.
    
    Expected error data:
     'InvalidRegistration'
     'NotRegistered'
    '''
    def log_exception(self, message):
        self._logger.info(message)


class AndroidDeviceSendMessageException(TaskException):
    '''
    Unexpected errors
    '''
    pass


class DeviceChannelInfoException(TaskException):
    '''
    When the database table does not have a record
    '''
    def log_exception(self, message):
        self._logger.info(message)


#@task(rate_limit="5000/s") # Better global limits??
@task
def send_message(device_channel_info_id, delay_while_idle=False, **kwargs):
    '''
    Sends a message to the device.
    
    delay_while_idle - If included, indicates that the message should not be 
                       sent immediately if the device is idle. The server will 
                       wait for the device to become active, and then only the 
                       last message for each collapse_key value will be sent.
    '''
    logger = send_message.get_logger(**kwargs)

    try:
        dci = DeviceChannelInfo.objects.get(pk=device_channel_info_id)
    except DeviceChannelInfo.DoesNotExist:
        raise DeviceChannelInfoException(('Record pk=%d not '
                                          'exists') % (device_channel_info_id))


    if dci.device.failed_push:
        logger.debug("Skip device 'Failed push' [DeviceChannelInfo id %d]" %
                     device_channel_info_id)
        return False

    values = {
        'registration_id': dci.device.registration_id,
        'collapse_key': dci.channel.collapse_key,
    }

    if delay_while_idle:
        values['delay_while_idle'] = ''

    for message in dci.channel.message.all():
        values['data.%s' % message.key_name] = message.data

    headers = {
        'Authorization': 'GoogleLogin auth=%s' % settings.C2DM_AUTH_TOKEN,
    }

    try:
        params = urllib.urlencode(values)
        request = urllib2.Request(C2DM_URL, params, headers)

        # Make the request
        response = urllib2.urlopen(request)

        if response.getcode() == 503:
            #server is temporarily unavailable. Wait Retry-After seconds
            retry_after = int(response.info().getheader('Retry-After', '0'))
            raise send_message.retry(countdown=retry_after)

        elif response.getcode() == 401:
            raise AndroidDeviceSendMessageException('ClientLogin AUTH_TOKEN is '
                                                    'invalid')

        result = [d.strip().lower() for d in response.read().split('=')]
        if 'error' in result:
            if result[1] == 'invalidregistration' or \
               result[1] == 'notregistered':
                dci.device.failed_push = True
                dci.device.save()
                raise AndroidDeviceNotRegisteredException(result[1])
            elif result[1] == 'quotaexceeded':
                # TODO: send an email
                raise AndroidDeviceSendMessageException(
                            'QuotaExceeded[dci=%d]: %s' %
                            (device_channel_info_id, result[1]))
            elif result[1] == 'devicequotaexceeded':
                # TODO: send an email
                raise AndroidDeviceSendMessageException(
                            'DeviceQuotaExceeded[dci=%d]: %s' %
                            (device_channel_info_id, result[1]))
            elif result[1] == 'messagetoobig':
                # TODO: write to database
                # TODO: send an email 
                raise AndroidDeviceSendMessageException(
                            'MessageTooBig[dci=%d]: %s' %
                            (device_channel_info_id, result[1]))
            elif result[1] == 'missingcollapsekey':
                # TODO: send an email
                raise AndroidDeviceSendMessageException(
                            'MissingCollapseKey[dci=%d]: %s' %
                            (device_channel_info_id, result[1]))
            else:
                # TODO: send an email
                raise AndroidDeviceSendMessageException(
                            'Unknown error code[dci=%d]: %s' %
                            (device_channel_info_id, result[1]))
        elif 'id' in result:
            from django.utils import timezone
            dci.last_message = timezone.now()
            dci.save()
            return True

    except URLError, error:
        message = 'URLError[dci=%d]: %s' % (device_channel_info_id, error,)
        raise AndroidDeviceSendMessageException(message)

    except SoftTimeLimitExceeded:
        logger.warning('SoftTimeLimitExceeded[dci=%d]: %s' %
                       (device_channel_info_id, error,))
        return False

    return False


