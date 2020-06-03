import logging

####################
# From Python 3.2.x source Lib/test/support.py
class TestHandler(logging.handlers.BufferingHandler):
    def __init__(self, matcher):
        # BufferingHandler takes a "capacity" argument
        # so as to know when to flush. As we're overriding
        # shouldFlush anyway, we can set a capacity of zero.
        # You can call flush() manually to clear out the
        # buffer.
        logging.handlers.BufferingHandler.__init__(self, 0)
        self.matcher = matcher

    def shouldFlush(self):
        return False

    def emit(self, record):
        self.format(record)
        self.buffer.append(record.__dict__)

    def matches(self, **kwargs):
        """
        Look for a saved dict whose keys/values match the supplied arguments.
        """
        return any(self.matcher.matches(d, **kwargs) for d in self.buffer)

class Matcher(object):

    _partial_matches = ('msg', 'message')

    def matches(self, d, **kwargs):
        """
        Try to match a single dict with the supplied arguments.

        Keys whose values are strings and which are in self._partial_matches
        will be checked for partial (i.e. substring) matches. You can extend
        this scheme to (for example) do regular expression matching, etc.
        """
        result = True
        for k in kwargs:
            v = kwargs[k]
            dv = d.get(k)
            if not self.match_value(k, dv, v):
                result = False
                break
        return result

    def match_value(self, k, dv, v):
        """
        Try to match a single stored value (dv) with a supplied value (v).
        """
        if type(v) != type(dv):
            result = False
        elif type(dv) is not str or k not in self._partial_matches:
            result = (v == dv)
        else:
            result = dv.find(v) >= 0
        return result
#
##########################


def make_fake_urlopen(code=200, response='', info={},
                        print_request=False):
    '''
    It creates a fake urlopen function.
    
    Usage:
    import <module>
    <module>.urllib2.urlopen = make_fake_urlopen()
    
    '''
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
