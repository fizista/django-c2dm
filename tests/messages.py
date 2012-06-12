import datetime
import logging
import hashlib
import inspect

from django.test import TestCase
from django.http import HttpRequest, HttpResponse, Http404
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.utils.timezone import utc
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from django_c2dm.models import AndroidDevice, MessageData, MessageChannels, \
                               MessageGroups, DeviceChannelInfo
from django_c2dm.message import standalone as msg_standalone
from django_c2dm.message import db as msg_db
from django_c2dm.message.db import FailedPushException
from django_c2dm.message.exceptions import *
from celery.exceptions import RetryTaskError
from django_c2dm.tests.adds import TestHandler, Matcher, make_fake_urlopen
from django_c2dm import tasks



def make_fake_get_logger(logger):
    '''
    It creates a fake tesk.get_logger function.
    
    Usage:
    import <tasks_module>
    <tasks_module>.<method>.get_logger = make_fake_get_logger(logger)
    
    '''
    def get_function(*args, **kwargs):
        return logger
    return get_function


class MessageTestCase(TestCase):

    def assertEqualSub(self, a, b , msg=None):
        self.assertEqual(a, b, msg or \
                 ('AssertionError[%s]: %s != %s\nFor test class %s') % \
                 (inspect.stack()[1][3], a, b, type(self).__name__))


class MessageRequestTest(MessageTestCase):

    def setUp(self):
        self.request = self.get_request()
        self.request.check_data() # should be ok
        self.request.set_logger(logging.getLogger('test_base_request'))

    def get_input_collapse_key(self):
        return 'collapse_key_01'

    def get_input_registration_id(self):
        return 'registration_id_01'

    def get_input_delay_while_idle(self):
        return False

    def get_input_data(self):
        return {'key1':'data1', 'key2':'data2'}

    def get_request(self):
        'return MessageRequest'
        raise NotImplementedError('get_request')

    def test_get_collapse_key(self):
        self.assertEqualSub(
                 self.request.get_collapse_key(),
                 self.get_input_collapse_key())

    def test_get_registration_id(self):
        self.assertEqualSub(
                 self.request.get_registration_id(),
                 self.get_input_registration_id())

    def test_get_delay_while_idle(self):
        self.assertEqualSub(
                 self.request.get_delay_while_idle(),
                 self.get_input_delay_while_idle())

    def test_get_data(self):
        self.assertEqualSub(
                 self.request.get_data(),
                 self.get_input_data())





class MessageDbRequestTest(MessageRequestTest):
    fixtures = ['test_messages.json']
    collapse_key_id = 100

    def setUp(self):
        MessageGroups(name='empty').save()
        MessageGroups(name='testing').save()
        super(MessageDbRequestTest, self).setUp()

    def get_input_data(self):
        data = super(MessageDbRequestTest, self).get_input_data()
        data[10] = 'num10'
        return data

    def get_input_collapse_key(self):
        collapse_key = super(MessageDbRequestTest, self).\
                             get_input_collapse_key()
        return hashlib.md5(collapse_key + str(self.collapse_key_id)).\
                            hexdigest()

    def get_request(self):
        'return MessageRequest'

        mc = MessageChannels(name=super(MessageDbRequestTest, self).\
                                        get_input_collapse_key())
        mc.id = self.collapse_key_id
        mc.save()

        for key, data in self.get_input_data().items():
            md = MessageData(data=data)
            if type(key) is int:
                md.id = key
            else:
                md.name = key
            md.save()
            mc.message.add(md)
        mc.save()

        mg = MessageGroups(name='test_all_db')
        mg.save()

        ad = AndroidDevice()
        ad.id = 1000
        ad.device_id = 'test_send_message_db_01'
        ad.registration_id = self.get_input_registration_id()
        ad.save()

        dci = DeviceChannelInfo()
        dci.device = ad
        dci.channel = mc
        dci.group = mg
        dci.save()

        return msg_db.MessageRequest(dci, self.get_input_delay_while_idle())

    def test_get_data(self):
        data = {}
        for k, d in self.get_input_data().items():
            if type(k) is int:
                data[hex(k)[2:]] = d
            else:
                data[k] = d
        self.assertEqualSub(
                 self.request.get_data(),
                 data)

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
                md = MessageData(data=('xy' * 5))
                md.save()
                too_much_data.message.add(md)
                too_much_data.full_clean()
                too_much_data.save()
            self.assertTrue(False, 'Except ValidationError') # pragma: no cover
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




class MessageStandAloneRequestTest(MessageRequestTest):

    def get_request(self):
        'return MessageRequest'
        return msg_standalone.MessageRequest(
                         self.get_input_collapse_key(),
                         self.get_input_registration_id(),
                         self.get_input_data(),
                         self.get_input_delay_while_idle())


class MessageResponseTest(MessageTestCase):

    def setUp(self):

        self.response = self.get_response()
        self.request = self.get_request()
        self.request.check_data() # should be ok
        self.request.set_logger(logging.getLogger('test_base_request'))
        self.response.set_request(self.request)

        # catch the all logging is
        self.handler = TestHandler(Matcher())
        self.logger = logging.getLogger('test_base_response')
        self.logger.addHandler(self.handler)
        self.response.set_logger(self.logger)

    def tearDown(self):
        #print self.handler.buffer
        self.logger.removeHandler(self.handler)
        self.handler.close()

    def get_request(self):
        raise NotImplementedError('get_request')

    def get_response(self):
        raise NotImplementedError('get_response')

    def test_error_invalid_registration(self):
        self.assertRaises(InvalidRegistrationException,
                          self.response.set_error, 'invalid_registration')

    def test_error_not_registered(self):
        self.assertRaises(NotRegisteredException,
                          self.response.set_error, 'not_registered', 'dtd')

    def test_error_quota_exceeded(self):
        self.assertRaises(QuotaExceededException,
                          self.response.set_error, 'quota_exceeded')

    def test_error_device_quota_exceeded(self):
        self.assertRaises(DeviceQuotaExceededException,
                          self.response.set_error, 'device_quota_exceeded')

    def test_error_message_too_big(self):
        self.assertRaises(MessageTooBigException,
                          self.response.set_error, 'message_too_big',)

    def test_error_missing_collapse_key(self):
        self.assertRaises(MissingCollapseKeyException,
                          self.response.set_error, 'missing_collapse_key', 'dtd')

    def test_error_unknown_error_code(self):
        self.assertRaises(UnknownErrorCodeException,
                          self.response.set_error, 'unknown_error_code')

    def test_error_url_error(self):
        self.assertRaises(UrlErrorException,
                          self.response.set_error, 'url_error', 'dtd')

    def test_error_invalid_auth_token(self):
        self.assertRaises(ErrorInvalidAuthTokenException,
                          self.response.set_error, 'invalid_auth_token', 'dtd')

    def test_error_invalid_response(self):
        self.assertRaises(InvalidResponseException,
                          self.response.set_error, 'invalid_response', 'dtd')

    def test_error_not_implemented(self):
        self.assertRaises(NotImplementedError,
                          self.response.set_error, 'qwerty', 'dtd')

    def test_get_result(self):
        self.response.set_result(111)
        self.assertEqual(self.response.get_result(), 111)


class MessageDbResponseTest(MessageResponseTest):
    fixtures = ['test_messages.json']

    def setUp(self):
        class MT(MessageDbRequestTest):
            def __init__(self):
                pass
        self.request_test = MT()
        self.request = self.request_test.get_request()
        super(MessageDbResponseTest, self).setUp()

    def get_request(self):
        return self.request

    def get_response(self):
        dci = DeviceChannelInfo.objects.get(pk=self.request._id)
        return msg_db.MessageResponse(dci)

class MessageStandAloneResponseTest(MessageResponseTest):

    def setUp(self):
        class MT(MessageStandAloneRequestTest):
            def __init__(self):
                pass
        self.request_test = MT()
        self.request = self.request_test.get_request()
        super(MessageStandAloneResponseTest, self).setUp()

    def get_request(self):
        return self.request

    def get_response(self):
        return msg_standalone.MessageResponse(
                 self.request._collapse_key,
                 self.request._registration_id,
                 self.request._data,
                 self.request._delay_while_idle)




class MessageSend(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

    def get_message(self):
        'Return (obj[type MessageRequest],object[type MessageResponse])'
        raise NotImplementedError('get_collapse_key')
        return message_request, message_response


    def test_http_resonse_200_success(self):
        tasks.urllib2.urlopen = make_fake_urlopen()

        tasks.urllib2.urlopen = make_fake_urlopen(response=' id  =   123  ')
        response = tasks.send_message(*self.get_message())
        self.assertEqual(response, 123)

    def test_http_resonse_503_fail(self):
        tasks.urllib2.urlopen = make_fake_urlopen()

        tasks.urllib2.urlopen = make_fake_urlopen(code=503)

        with self.assertRaises(RetryTaskError):
            tasks.send_message(*self.get_message())

    def test_http_resonse_401_fail_InvalidAuthToken(self):
        tasks.urllib2.urlopen = make_fake_urlopen()

        tasks.urllib2.urlopen = make_fake_urlopen(code=401)

        with self.assertRaises(ErrorInvalidAuthTokenException):
            tasks.send_message(*self.get_message())

    def test_http_resonse_200_fail_InvalidRegistration(self):
        tasks.urllib2.urlopen = make_fake_urlopen()

        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response='Error=InvalidRegistration')

        with self.assertRaises(InvalidRegistrationException):
            tasks.send_message(*self.get_message())

    def test_http_resonse_200_fail_NotRegistered(self):
        tasks.urllib2.urlopen = make_fake_urlopen()

        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response='  Error =   NotRegistered ')

        with self.assertRaises(NotRegisteredException):
            tasks.send_message(*self.get_message())

    def test_http_resonse_200_fail_QuotaExceeded(self):
        tasks.urllib2.urlopen = make_fake_urlopen()

        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response='  Error =   QuotaExceeded ')

        with self.assertRaises(QuotaExceededException):
            tasks.send_message(*self.get_message())

    def test_http_resonse_200_fail_DeviceQuotaExceeded(self):
        tasks.urllib2.urlopen = make_fake_urlopen()

        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response='  Error =DeviceQuotaExceeded ')

        with self.assertRaises(DeviceQuotaExceededException):
            tasks.send_message(*self.get_message())

    def test_http_resonse_200_fail_MessageTooBig(self):
        tasks.urllib2.urlopen = make_fake_urlopen()

        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response='  Error =MessageTooBig ')

        with self.assertRaises(MessageTooBigException):
            tasks.send_message(*self.get_message())


    def test_http_resonse_200_fail_MissingCollapseKey(self):
        tasks.urllib2.urlopen = make_fake_urlopen()

        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response='  Error =MissingCollapseKey ')

        with self.assertRaises(MissingCollapseKeyException):
            tasks.send_message(*self.get_message())

    def test_http_resonse_200_fail_UnknownCodeXX(self):
        tasks.urllib2.urlopen = make_fake_urlopen()

        tasks.urllib2.urlopen = make_fake_urlopen(
                                  response='  Error =UnknownCodeXX ')

        with self.assertRaises(UnknownErrorCodeException):
            tasks.send_message(*self.get_message())


class MessageStandAloneSend(MessageSend):

    def setUp(self):
        self.handler = TestHandler(Matcher())
        self.logger = logging.getLogger('test_base_response')
        self.logger.addHandler(self.handler)
        tasks.send_message.get_logger = make_fake_get_logger(self.logger)
        super(MessageStandAloneSend, self).setUp()

    def tearDown(self):
        #print self.handler.buffer
        self.logger.removeHandler(self.handler)
        self.handler.close()
        super(MessageStandAloneSend, self).tearDown()

    def get_message(self):
        collapse_key = 'col_key'
        registration_id = 'reg_id'
        data = {'key1':'data1', 'key2':'data2'}
        delay_while_idle = True
        message_request = msg_standalone.MessageRequest(collapse_key,
                            registration_id, data, delay_while_idle)
        message_response = msg_standalone.MessageResponse(collapse_key,
                            registration_id, data, delay_while_idle)
        return message_request, message_response


class MessageDbSend(MessageSend):
    fixtures = ['test_messages.json']

    def setUp(self):
        self.handler = TestHandler(Matcher())
        self.logger = logging.getLogger('test_base_response')
        self.logger.addHandler(self.handler)
        tasks.send_message.get_logger = make_fake_get_logger(self.logger)
        super(MessageDbSend, self).setUp()

    def tearDown(self):
        #print self.handler.buffer
        self.logger.removeHandler(self.handler)
        self.handler.close()
        super(MessageDbSend, self).tearDown()

    def get_message(self):
        self.collapse_key = 'col_key'
        self.registration_id = 'reg_id'
        self.data_in = {'key1':'data1', 'key2':'data2'}
        self.delay_while_idle = False

        mc = MessageChannels(name=self.collapse_key)
        mc.id = 100
        mc.save()

        for key, data in self.data_in.items():
            md = MessageData(data=data)
            if type(key) is int:
                md.id = key
            else:
                md.name = key
            md.save()
            mc.message.add(md)
        mc.save()

        mg = MessageGroups(name='test_all_db')
        mg.save()

        ad = AndroidDevice()
        ad.id = 1000
        ad.device_id = 'test_send_message_db_01'
        ad.registration_id = self.registration_id
        ad.save()

        dci = DeviceChannelInfo()
        dci.device = ad
        dci.channel = mc
        dci.group = mg
        dci.save()

        self.dci_id = dci.id

        message_request = msg_db.MessageRequest(dci, self.delay_while_idle)
        message_response = msg_db.MessageResponse(dci)

        return message_request, message_response

    def test_no_record_in_db_device_channel_info(self):
        message_request, message_response = self.get_message()
        dci = DeviceChannelInfo.objects.get(pk=message_request._id)
        dci.delete()

        with self.assertRaises(ObjectDoesNotExist):
            tasks.send_message(message_request, message_response)

    def test_failed_push_in_db(self):
        message_request, message_response = self.get_message()
        dci = DeviceChannelInfo.objects.get(pk=message_request._id)
        dci.device.failed_push = True
        dci.device.save()

        with self.assertRaises(FailedPushException):
            tasks.send_message(message_request, message_response)

    def test_http_resonse_200_fail_InvalidRegistration(self):
        super(MessageDbSend, self).\
                        test_http_resonse_200_fail_InvalidRegistration()

        dci = DeviceChannelInfo.objects.get(pk=self.dci_id)
        self.assertTrue(dci.device.failed_push)

    def test_http_resonse_200_fail_NotRegistered(self):
        super(MessageDbSend, self).\
                        test_http_resonse_200_fail_NotRegistered()

        dci = DeviceChannelInfo.objects.get(pk=self.dci_id)
        self.assertTrue(dci.device.failed_push)

    def test_http_resonse_200_success(self):
        pre_last_message = timezone.now()
        super(MessageDbSend, self).\
                        test_http_resonse_200_success()

        ## 200 ID check last change     
        dci = DeviceChannelInfo.objects.get(pk=self.dci_id)
        self.assertTrue(dci.last_message > pre_last_message)








