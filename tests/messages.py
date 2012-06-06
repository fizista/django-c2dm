import datetime

from django.test import TestCase
from django.http import HttpRequest, HttpResponse, Http404
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.utils.timezone import utc
from django.utils import timezone

from django_c2dm.models import AndroidDevice, MessageData, MessageChannels, \
                               MessageGroups, DeviceChannelInfo

from celery.exceptions import RetryTaskError

class MessageTest(TestCase):
    fixtures = ['test_messages.json']

    def setUp(self):
        MessageGroups(name='empty').save()
        MessageGroups(name='testing').save()

    def test_create_channel(self):
        # empty
        m = MessageChannels(name='empty')
        m.save()
        self.assertEqual(MessageChannels.objects.get(pk=m.pk).name, 'empty')

        # duplicate
        self.assertRaises(IntegrityError, MessageChannels(name='empty').save)


        # some data
        some_data = MessageChannels(name='some_data')
        some_data.save()
        md = MessageData(data='aaa')
        md.save()
        some_data.message.add(md)
        md = MessageData(name='aaa', data='aaa2')
        md.save()
        some_data.message.add(md)
        some_data.save()
        self.assertEqual(
             len(MessageChannels.objects.get(pk=some_data.pk).message.all()), 2)
        self.assertEqual(
             MessageChannels.objects.get(pk=some_data.pk).name, 'some_data')

        #too much data
        too_much_data = MessageChannels(name='too_much_data')
        too_much_data.save()
        try:
            for i in range(1, 1000):
                ValidationError('ok')
                md = MessageData(data=('xy' * 5))
                md.save()
                too_much_data.message.add(md)
                too_much_data.full_clean()
                too_much_data.save()
            self.assertTrue(False, 'Except ValidationError')
        except ValidationError:
            self.assertTrue(True)

        #  change data
        change_data = MessageChannels(name='change_data')
        change_data.save()
        md = MessageData(data='aaa')
        md.save()
        pk_last_change = md.pk
        change_data.message.add(md)
        change_data.save()
        change_data = MessageChannels.objects.get(pk=change_data.pk)
        self.assertEqual(md.last_change,
                         change_data.last_change)

        md = MessageData(data='bbb') # add new
        md.save()
        change_data.message.add(md)
        change_data.save()
        change_data = MessageChannels.objects.get(pk=change_data.pk)
        self.assertEqual(md.last_change,
                         change_data.last_change)

        md = MessageData.objects.get(pk=pk_last_change)
        md.data = 'aaaAAA'
        md.save()
        self.assertEqual(md.last_change,
                         change_data.last_change)

        # when missing change
        change_data = MessageChannels(name='change_data_missing')
        change_data.save()
        change_data = MessageChannels.objects.get(pk=change_data.pk)
        self.assertEqual(None,
                         change_data.last_change)


    def test_send_message(self):

        # some data
        mc = MessageChannels(name='mc')
        mc.save()
        md = MessageData(data='1234567890')
        md.save()
        mc.message.add(md)
        md = MessageData(name='a', data='abcdefghijklmnoprstuwxyz')
        md.save()
        mc.message.add(md)
        mc.save()

        mg = MessageGroups(name='test_all')
        mg.save()

        ad = AndroidDevice()
        ad.device_id = 'test_send_message_01'
        ad.registration_id = 'test_send_message_01_reg_id'
        ad.save()

        dci = DeviceChannelInfo()
        dci.device = ad
        dci.channel = mc
        dci.group = mg
        dci.save()

        def make_fake_urlopen(code=200, response='', info={},
                                print_request=False):
            def fake_urlopen(request):
                if print_request:
                    print request
                class FakeInfo():
                    _info = info
                    def getheader(self, name, default=None):
                        return self._info.get(name) or default
                class FakeResponse():
                    def __init__(self, request):
                        self._request = request
                        self._response = response
                        self._info = {'content-type': 'text/xml; charset=utf-8'}
                        self._info.update(info)
                        self._code = code
                    def getcode(self):
                        return self._code
                    def read(self):
                        return self._response
                    def info(self):
                        return FakeInfo()
                return FakeResponse(request)
            return fake_urlopen

        from django_c2dm import tasks
        tasks.urllib2.urlopen = make_fake_urlopen()

        ### Exceptions

        ## bad DeviceChannelInfo ID
        self.assertRaises(tasks.DeviceChannelInfoException,
                          tasks.send_message,
                          999999)


        ## failed push in table
        ad.failed_push = True
        ad.save()
        self.assertFalse(tasks.send_message(dci.id))
        ad.failed_push = False
        ad.save()

        ## check request data
        ## ??
        tasks.urllib2.urlopen = make_fake_urlopen(print_request=True)

        ### RESPONSE

        ## 503
        tasks.urllib2.urlopen = make_fake_urlopen(code=503)
        self.assertRaises(RetryTaskError,
                          tasks.send_message,
                          dci.id)

        ## 401
        tasks.urllib2.urlopen = make_fake_urlopen(code=401)
        self.assertRaises(tasks.AndroidDeviceSendMessageException,
                          tasks.send_message,
                          dci.id)

        ## 200 InvalidRegistration / NotRegistered
        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response='Error=InvalidRegistration')
        self.assertRaises(tasks.AndroidDeviceNotRegisteredException,
                          tasks.send_message,
                          dci.id)
        dci = DeviceChannelInfo.objects.get(pk=dci.id)
        self.assertTrue(dci.device.failed_push)
        dci.device.failed_push = False
        dci.device.save()

        ## 200 QuotaExceeded
        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response='Error=  QuotaExceeded')
        self.assertRaisesRegexp(tasks.AndroidDeviceSendMessageException,
                                r'QuotaExceeded.*',
                                tasks.send_message,
                                dci.id)

        ## 200 DeviceQuotaExceeded
        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response='Error  =  DeviceQuotaExceeded')
        self.assertRaisesRegexp(tasks.AndroidDeviceSendMessageException,
                                r'DeviceQuotaExceeded.*',
                                tasks.send_message,
                                dci.id)

        ## 200 MessageTooBig
        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response=' Error  =  MessageTooBig')
        self.assertRaisesRegexp(tasks.AndroidDeviceSendMessageException,
                                r'MessageTooBig.*',
                                tasks.send_message,
                                dci.id)

        ## 200 MissingCollapseKey
        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response=' Error  =  MissingCollapseKey  ')
        self.assertRaisesRegexp(tasks.AndroidDeviceSendMessageException,
                                r'MissingCollapseKey.*',
                                tasks.send_message,
                                dci.id)

        ## 200 Unknown Error
        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response=' Error  =  UError XXX  ')
        self.assertRaisesRegexp(tasks.AndroidDeviceSendMessageException,
                                r'Unknown error.*',
                                tasks.send_message,
                                dci.id)

        ## 200 ID OK
        tasks.urllib2.urlopen = make_fake_urlopen(response=' id  =   123  ')
        pre_last_message = timezone.now()
        self.assertTrue(tasks.send_message(dci.id))

        ## 200 ID check last change     
        dci = DeviceChannelInfo.objects.get(pk=dci.id)
        self.assertTrue(dci.last_message > pre_last_message)






