import logging

from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ValidationError
from django.shortcuts import Http404
from django.contrib.messages.api import get_messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django_c2dm.models import AndroidDevice, AndroidDeviceToken, \
                                REGISTRATION_TOKEN_LEN
from django_c2dm.message.standalone import MessageRequest, MessageResponse
from django_c2dm.tasks import send_message
from django_c2dm.message import standalone as msg_standalone
from django_c2dm.message import db as msg_db

logger = logging.getLogger('django.c2dm')

COLLAPSE_KEY_REGISTRATION_TOKEN = 'registration_token'

def send_registration_token(android_device_id, registration_id):
    '''
    Return task object
    '''
    # If there is such device, then we put off to the queue
    # ("registration_id"), and wait for confirm registration.
    ad = AndroidDevice.objects.get(pk=android_device_id)
    adt = AndroidDeviceToken()
    adt.device = ad
    adt.registration_id = registration_id
    adt.full_clean()
    adt.save()

    # send token
    collapse_key = COLLAPSE_KEY_REGISTRATION_TOKEN
    registration_id = adt.registration_id
    data = {COLLAPSE_KEY_REGISTRATION_TOKEN: adt.token}
    delay_while_idle = True

    message_request = msg_standalone.MessageRequest(collapse_key,
                        registration_id, data, delay_while_idle)
    message_response = msg_db.MessageResponseStandAlone(android_device_id)
    return send_message.delay(message_request, message_response)

def register_device(device_id, registration_token):
    'Return True if success'
    try:
        adt = AndroidDeviceToken.objects.filter(
                                device__device_id=device_id,
                                token=registration_token)[0]
        adt.confirm = True
        adt.device.registration_id = adt.registration_id
        adt.device.failed_push = False
        adt.device.save()
        adt.save()
        return True
    except Exception, e:
        logger.info('Register device fail [%s]' % e)
        return False

@csrf_exempt
def set_registration_id(request):
    """Registration application"""

    if request.method == 'GET':

        try:
            device_id = request.GET['device_id']
            registration_id = request.GET['registration_id']
            # Check mimimum length
            if len(device_id) < 8:
                logger.info('DeviceId too short [%s]' % (device_id,))
                return HttpResponse(status=400)

            if len(registration_id) < 8:
                logger.info('Registration id too short [%s]' %
                                (registration_id,))
                return HttpResponse(status=400)

        except KeyError, e:
            # When the input parameters are wrong, the script 
            # is terminated code http 400th
            logger.info('KeyError [%s] [%s]' % (e, request.GET,))
            return HttpResponse(status=400)

        try:
            # We check the database if they already have such 
            # device with a given ID
            ad = AndroidDevice.objects.filter(
                                     device_id=device_id)[0]

            task_registration = send_registration_token(ad.id, registration_id)

            logger.info('Registration device is in the queue '
                        '[ad=%s,regid=%s]' %
                                (device_id, registration_id))

            response = HttpResponse(status=200)
            response.task_registration = task_registration
            return response

        except ValidationError, e:

            logger.debug('ValidationError [%s]' % e)
            return HttpResponse(status=400)

        except IndexError:
            # Registration new device
            try:
                ad = AndroidDevice()
                ad.device_id = request.GET['device_id']
                ad.full_clean()
                ad.save()

                task_registration = send_registration_token(ad.id,
                                                          registration_id)

                logger.info('Re-registration device is in the queue'
                            ' [ad=%s,regid=%s]' %
                                (device_id, registration_id))

                response = HttpResponse(status=200)
                response.task_registration = task_registration
                return response

            except ValidationError, e:

                logger.debug('ValidationError [%s]' % e)
                return HttpResponse(status=400)

        return HttpResponse(status=501)
    # POST,... http 404
    raise Http404

@csrf_exempt
def check_token(request):
    """Check registration token"""

    if request.method == 'GET':
        try:
            device_id = request.GET['device_id']
            registration_token = request.GET['registration_token']
            # Check mimimum length
            if len(device_id) < 8:
                logger.info('DeviceId too short [ad=%s]' % (device_id,))
                return HttpResponse(status=400)

            if len(registration_token) != REGISTRATION_TOKEN_LEN:
                logger.info('Registration token wrong length [token=%s]' %
                            (registration_token,))
                return HttpResponse(status=400)

        except KeyError, e:
            # When the input parameters are wrong, the script 
            # is terminated code http 400th
            logger.info('KeyError [%s] [%s]' % (e, request.GET,))
            return HttpResponse(status=400)

        if register_device(device_id, registration_token):
            logger.info('Successful re-registration [ad=%s, token=%s]' %
                                (device_id, registration_token))
            return HttpResponse(status=200)
        else:
            logger.info('Failed to re-register [ad=%s, token=%s]' %
                        (device_id, registration_token))
            return HttpResponse(status=400)

    # POST,... http 404
    raise Http404
