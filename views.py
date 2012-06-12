import logging

from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ValidationError
from django.shortcuts import Http404
from django.contrib.messages.api import get_messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import AndroidDevice

logger = logging.getLogger('django.c2dm')

@csrf_exempt
def set_registration_id(request):
    """Registration application"""

    if request.method == 'GET':

        try:
            device_id = request.GET['device_id']
            registration_id = request.GET['registration_id']

        except KeyError, e:
            # When the input parameters are wrong, the script 
            # is terminated code http 400th
            logger.debug('KeyError [%s] [%s]' % (e, request.GET,))
            return HttpResponse(status=400)

        try:
            # We check the database if they already have such 
            # device with a given ID
            ad = AndroidDevice.objects.filter(
                                     device_id=request.GET['device_id'])[0]
            # If there is such device, then we update "registration_id"
            ad.registration_id = request.GET['registration_id']
            ad.full_clean()
            ad.save()
            logger.info('Device re-registered [%s]' % device_id)

        except ValidationError, e:

            logger.debug('ValidationError [%s]' % e)
            return HttpResponse(status=400)

        except IndexError:

            try:
                ad = AndroidDevice()
                ad.device_id = request.GET['device_id']
                ad.registration_id = request.GET['registration_id']
                ad.full_clean()
                ad.save()
                logger.info('Device registered [%s]' % device_id)

            except ValidationError:

                logger.debug('ValidationError [%s]' % e)
                return HttpResponse(status=400)

        return HttpResponse(status=200)

    raise Http404

