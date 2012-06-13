from mock import patch

from django.utils import unittest
from django.http import HttpRequest, HttpResponse, Http404
from django.utils import timezone

from django_c2dm.models import AndroidDevice, AndroidDeviceToken, \
                                REGISTRATION_TOKEN_LEN
from django_c2dm import views
from django_c2dm.tests.adds import make_fake_urlopen

import logging
logging.disable(logging.CRITICAL) # logging off / almost

class RegistrationTest(unittest.TestCase):

    def setUp(self):
        AndroidDevice.objects.all().delete()

    def test_create_tokens(self):
        ad = AndroidDevice()
        ad.device_id = 'devid_553623'
        ad.save()

        pre_time = timezone.now()
        adt = AndroidDeviceToken()
        adt.device = ad
        adt.save()

        adt = AndroidDeviceToken.objects.get(id=adt.id)

        self.assertTrue(pre_time < adt.change_date)
        self.assertFalse(adt.confirm)
        self.assertTrue(len(adt.token) == REGISTRATION_TOKEN_LEN)

        adt2 = AndroidDeviceToken()
        adt2.device = ad
        adt2.save()

        self.assertNotEqual(adt.token, adt2.token)


    def test_register_device(self):
        # Create new device
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {
                       'device_id': 'devid_001',
                       'registration_id': 'reg_id_001'}
        # register device
        with patch('urllib2.urlopen') as urlopen:
            urlopen.return_value = make_fake_urlopen(
                                     response='id=123')(request)
            response = views.set_registration_id(request)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)

        ad = AndroidDevice.objects.get(device_id='devid_001')
        self.assertEqual(ad.registration_id, '')

        # wait to the time to send a token
        task = response.task_registration
        res = task.wait()

        adt = AndroidDeviceToken.objects.get(registration_id='reg_id_001')
        self.assertTrue(len(adt.token) == REGISTRATION_TOKEN_LEN)

        # check token
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {
                       'device_id': 'devid_001',
                       'registration_token': adt.token}

        response = views.check_token(request)
        self.assertEqual(response.status_code, 200)

        # check if has been set registration_id
        ad = AndroidDevice.objects.get(registration_id='reg_id_001')
        self.assertEqual('devid_001', ad.device_id)

        ##############################
        # update registration_id

        # Create new device
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {
                       'device_id': 'devid_001',
                       'registration_id': 'reg_id_002'}
        # register device
        with patch('urllib2.urlopen') as urlopen:
            urlopen.return_value = make_fake_urlopen(
                                         response='id=1234')(request)
            response = views.set_registration_id(request)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)

        ad = AndroidDevice.objects.get(device_id='devid_001')
        self.assertEqual(ad.registration_id, 'reg_id_001')

        # wait to the time to send a token
        task = response.task_registration
        task.wait()

        adt = AndroidDeviceToken.objects.get(registration_id='reg_id_002')
        self.assertTrue(len(adt.token) == REGISTRATION_TOKEN_LEN)

        # check token
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {
                       'device_id': 'devid_001',
                       'registration_token': adt.token}

        response = views.check_token(request)
        self.assertEqual(response.status_code, 200)

        # check if has been set registration_id
        ad = AndroidDevice.objects.get(registration_id='reg_id_002')
        self.assertEqual('devid_001', ad.device_id)

    def assertInputOutput(self, get, code=200, response='id=123'):
        request = HttpRequest()
        request.method = 'GET'
        request.GET = get
        # register device
        with patch('urllib2.urlopen') as urlopen:
            urlopen.return_value = make_fake_urlopen(
                                     response=response)(request)
            response = views.set_registration_id(request)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, code)

    def test_check_input_parametrs(self):
        # minimum device_id
        self.assertInputOutput(
                       {
                       'device_id': '1234',
                       'registration_id': '123456789'
                       },
                       400)

        # minimum registration_id
        self.assertInputOutput(
                       {
                       'device_id': '1234567890',
                       'registration_id': '1234'
                       },
                       400)

        # maximum registration_id
        self.assertInputOutput(
                       {
                       'device_id': '1234567890',
                       'registration_id': ''.join([str(i % 10)
                                                   for i in range(150)])
                       },
                       400)

        # maximum device_id
        self.assertInputOutput(
                       {
                       'device_id': ''.join([str(i % 10)
                                                   for i in range(150)]),
                       'registration_id': '123456789'
                       },
                       400)

        # keyerror no parameter 'devoce_id'
        self.assertInputOutput(
                       {
                       'registration_id': '123456789'
                       },
                       400)

        # keyerror no parameter 'devoce_id'
        self.assertInputOutput(
                       {
                       'device_id': '123456789'
                       },
                       400)


    def off_test_register_device_fail(self):
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
        self.assertIsInstance(response, HttpResponse)
        ad = AndroidDevice.objects.all()
        self.assertEqual(response.status_code, 400)

        # no data
        request = HttpRequest()
        request.method = 'GET'
        response = set_registration_id(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 400)

    def off_test_update_registration_id(self):
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {
                       'device_id': 'devid_001',
                       'registration_id': 'reg_id_001'}
        response = set_registration_id(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)





