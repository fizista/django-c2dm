from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ValidationError
from django.shortcuts import Http404
from django.contrib.messages.api import get_messages

from .models import AndroidDevice

def set_registration_id(request):
    """Registration application"""

    if request.method == 'GET':

        try:
            device_id = request.GET['device_id']
            registration_id = request.GET['registration_id']
        except KeyError:
            # When the input parameters are wrong, the script 
            # is terminated code http 400th
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

        except ValidationError:

            return HttpResponse(status=400)

        except IndexError:

            try:
                ad = AndroidDevice()
                ad.device_id = request.GET['device_id']
                ad.registration_id = request.GET['registration_id']
                ad.full_clean()
                ad.save()

            except ValidationError:

                return HttpResponse(status=400)

        return HttpResponse(status=200)

    raise Http404

