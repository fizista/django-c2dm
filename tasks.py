import hashlib
import urllib, urllib2
from urllib2 import URLError, HTTPError

from celery.exceptions import SoftTimeLimitExceeded
from celery.decorators import task

from django_c2dm.models import DeviceChannelInfo
from django_c2dm import settings

C2DM_URL = 'https://android.apis.google.com/c2dm/send'

@task
def send_message(message_request, message_response, **kwargs):
    '''
    Sends a message to the device.
    
    message_request - object MessageRequest
    message_response - object MessageResponse
    '''
    logger = send_message.get_logger(**kwargs)
    message_request.set_logger(logger)
    message_response.set_logger(logger)
    message_response.set_request(message_request)

    if message_response.get_task_id() == None:
        message_response.set_task_id(send_message.request.id)

    message_request.check_data()

    values = {
        'registration_id': message_request.get_registration_id(),
        'collapse_key': message_request.get_collapse_key(),
    }

    if message_request.get_delay_while_idle():
        values['delay_while_idle'] = ''

    for msg_key, msg_data in message_request.get_data().items():
        values['data.%s' % msg_key] = msg_data

    headers = {
        'Authorization': 'GoogleLogin auth=%s' % settings.C2DM_AUTH_TOKEN,
    }

    try:
        params = urllib.urlencode(values)
        request = urllib2.Request(C2DM_URL, params, headers)

        # Make the request
        try:
            response = urllib2.urlopen(request)
            response_code = response.getcode()

        except HTTPError, error:
            response_code = error.code

        except URLError, error:
            logger.error(('URLError: '
                           'RegID [%s], CollapseKey [%s], error: %s') % \
                           (message_request.get_registration_id(),
                            message_request.get_collapse_key(), error))
            message_response.set_error('url_error', unicode(error))
            return False

        if response_code == 503:
            #server is temporarily unavailable. Wait Retry-After seconds
            retry_after = int(response.info().getheader('Retry-After', '60'))
            raise send_message.retry(countdown=retry_after)

        elif response_code == 401:
            try:
                settings.C2DM_AUTH_TOKEN.renew()
                raise send_message.retry(countdown=5)
            except:
                message_response.set_error('invalid_auth_token',
                                       'ClientLogin AUTH_TOKEN is invalid')
        elif response_code == 200:
            pass
        else:
            raise UnknownHttpErrorCodeException('Http error code: %i' % response.getcode())

        try:
            response_data = response.read()
            key, data = [d.strip().lower() for d in response_data.split('=')]
        except:
            message_response.set_error('invalid_response', 'Response: %s' %
                                       response_data)
        if 'error' == key:
            if data == 'invalidregistration':
                message_response.set_error('invalid_registration')
            elif data == 'notregistered':
                message_response.set_error('not_registered')
            elif data == 'quotaexceeded':
                message_response.set_error('quota_exceeded')
            elif data == 'devicequotaexceeded':
                message_response.set_error('device_quota_exceeded')
            elif data == 'messagetoobig':
                message_response.set_error('message_too_big')
            elif data == 'missingcollapsekey':
                message_response.set_error('missing_collapse_key')
            elif data == 'mismatchsenderid':
                message_response.set_error('mismatch_sender_id')
            else:
                message_response.set_error('unknown_error_code',
                                           'Error [%s]' % (data,))
            return False
        elif 'id' in key:
            message_response.set_result(data)
            return data
        else:
            message_response.set_error('invalid_response', 'Response: %s' %
                                       response_data)
            return False

    except SoftTimeLimitExceeded:
        logger.warning(('SoftTimeLimitExceeded: '
                       'RegID [%s], CollapseKey [%s]') % \
                       (message_request.get_registration_id(),
                        message_request.get_collapse_key(),))
        return False

    return False

