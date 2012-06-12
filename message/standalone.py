from django_c2dm.message import base


class MessageRequest(base.MessageRequest):

    def __init__(self, collapse_key, registration_id, data,
                  delay_while_idle=True):
        self._collapse_key = collapse_key
        self._registration_id = registration_id
        self._delay_while_idle = delay_while_idle
        self._data = data
        super(MessageRequest, self).__init__()

    def get_collapse_key(self):
        return self._collapse_key

    def get_registration_id(self):
        return self._registration_id

    def get_delay_while_idle(self):
        return self._delay_while_idle

    def get_data(self):
        return self._data


class MessageResponse(base.MessageResponse):

    def __init__(self, collapse_key, registration_id, data,
                  delay_while_idle=True):
        self._collapse_key = collapse_key
        self._registration_id = registration_id
        self._delay_while_idle = delay_while_idle
        self._data = data
        super(MessageResponse, self).__init__()

