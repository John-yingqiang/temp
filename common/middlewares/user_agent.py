from django.utils.functional import SimpleLazyObject
from django_user_agents.utils import get_user_agent



def _get_os(request):
    uas = request.user_agent.ua_string
    if 'okhttp/' in uas:
        oss = 'android'
    elif ',iOS' in uas:
        oss = 'ios'
    else:
        oss = request.user_agent.os.family.lower()

    if 'MicroMessenger' in uas:
        oss += '-wechat'
    return oss


def user_agent_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        request.user_agent = SimpleLazyObject(lambda: get_user_agent(request))
        request.ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(', ')[-1] or request.META.get('REMOTE_ADDR')
        request.get_os = lambda: _get_os(request)

        response = get_response(request)
        return response

    return middleware
