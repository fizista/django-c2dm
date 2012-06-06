
from django.conf import settings

try:
    C2DM_AUTH_TOKEN = getattr(settings, 'C2DM_AUTH_TOKEN')
except AttributeError:
    raise BaseException('C2DM_AUTH_TOKEN required')

