from django.utils import unittest
from django.http import HttpRequest, HttpResponse, Http404

from django_c2dm.models import AndroidDevice
from django_c2dm.views import set_registration_id

class RegistrationTest(unittest.TestCase):

    def setUp(self):
        AndroidDevice.objects.all().delete()

    def test_register_device(self):
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {
                       'device_id': 'devid_001',
                       'registration_id': 'reg_id_001'}
        response = set_registration_id(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        ad = AndroidDevice.objects.get(device_id='devid_001')
        self.assertEqual(ad.registration_id, 'reg_id_001')

    def test_register_device_fail(self):
        # Bad method
        request = HttpRequest()
        request.method = 'POST'
        self.assertRaises(Http404, set_registration_id, request)

        # Too long data
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {
                       'device_id': 'devid_001_very long text..very long text..very long text..very long text..very long text..very long text',
                       'registration_id': 'reg_id_001'}
        response = set_registration_id(request)

        # no data
        request = HttpRequest()
        request.method = 'GET'
        response = set_registration_id(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 400)

    def test_update_registration_id(self):
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {
                       'device_id': 'devid_001',
                       'registration_id': 'reg_id_001'}
        response = set_registration_id(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)





