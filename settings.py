
from django.conf import settings
try:
    C2DM_AUTH_USER = getattr(settings, 'C2DM_AUTH_USER')
    C2DM_AUTH_PASSWORD = getattr(settings, 'C2DM_AUTH_PASSWORD')
    C2DM_AUTH_ACCOUNT_TYPE = getattr(settings, 'C2DM_AUTH_ACCOUNT_TYPE', 'GOOGLE')
    C2DM_AUTH_APP_NAME = getattr(settings, 'C2DM_AUTH_APP_NAME')
    from django_c2dm.message.auth import TokensManager
    C2DM_AUTH_TOKEN = TokensManager(
                                C2DM_AUTH_USER,
                                C2DM_AUTH_PASSWORD,
                                C2DM_AUTH_ACCOUNT_TYPE,
                                C2DM_AUTH_APP_NAME)
except AttributeError:
    try:
        C2DM_AUTH_TOKEN = getattr(settings, 'C2DM_AUTH_TOKEN')
    except AttributeError:
        raise BaseException('C2DM_AUTH_TOKEN required')

