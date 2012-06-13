from django_c2dm.message import base
from django_c2dm.message.exceptions import TaskException
from django_c2dm.models import DeviceChannelInfo, AndroidDevice


class FailedPushException(TaskException): pass


class MessageRequest(base.MessageRequest):

    def __init__(self, obj_dci, delay_while_idle=True):
        self._id = obj_dci.id
        self._collapse_key = obj_dci.channel.collapse_key
        self._registration_id = obj_dci.device.registration_id
        self._delay_while_idle = delay_while_idle
        self._data = dict([(m.key_name(), m.data)
                           for m in obj_dci.channel.message.all()])
        self.check_data()
        super(MessageRequest, self).__init__()

    def check_data(self):
        dci = DeviceChannelInfo.objects.get(pk=self._id)
        if dci.device.failed_push:
            raise FailedPushException(
                              "Failed push [DeviceChannelInfo id %d]" %
                               self._id,
                               self._logger)

    def get_collapse_key(self):
        return self._collapse_key

    def get_registration_id(self):
        return self._registration_id

    def get_delay_while_idle(self):
        return self._delay_while_idle

    def get_data(self):
        return self._data


class MessageResponse(base.MessageResponse):

    def __init__(self, obj_dci):
        self._id = obj_dci.id
        super(MessageResponse, self).__init__()

    def set_failed_push(self):
        try:
            dci = DeviceChannelInfo.objects.get(pk=self._id)
            dci.device.failed_push = True
            dci.device.save()
        except DeviceChannelInfo.DoesNotExist:
            pass
        except AndroidDevice.DoesNotExist:
            pass

    def set_result(self, id):
        from django.utils import timezone
        try:
            dci = DeviceChannelInfo.objects.get(pk=self._id)
            dci.last_message = timezone.now()
            dci.save()
        except DeviceChannelInfo.DoesNotExist:
            pass
        except AndroidDevice.DoesNotExist:
            pass
        super(MessageResponse, self).set_result(id)

    def error_invalid_registration(self):
        self.set_failed_push()
        super(MessageResponse, self).error_invalid_registration()

    def error_not_registered(self):
        self.set_failed_push()
        super(MessageResponse, self).error_not_registered()

class MessageResponseStandAlone(base.MessageResponse):

    def __init__(self, device_id):
        self._device_id = device_id
        super(MessageResponseStandAlone, self).__init__()

    def set_failed_push(self):
        try:
            ad = AndroidDevice.objects.get(pk=self._device_id)
            ad.failed_push = True
            ad.save()
        except DeviceChannelInfo.DoesNotExist:
            pass
        except AndroidDevice.DoesNotExist:
            pass

    def error_invalid_registration(self):
        self.set_failed_push()
        super(MessageResponseStandAlone, self).error_invalid_registration()

    def error_not_registered(self):
        self.set_failed_push()
        super(MessageResponseStandAlone, self).error_not_registered()

