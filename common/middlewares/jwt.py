from django.utils.functional import SimpleLazyObject
import jwt
import os
from django_user_agents.utils import get_user_agent
from django.core.exceptions import PermissionDenied
from ..phone_transform import normal_2_internal

TOKEN_SECRET = os.environ['TOKEN_SECRET']


def _get_token(request):
    """
    Returns the user model instance associated with the given request cookie.
    """
    token = request.COOKIES.get('ctoken')
    data = {}
    if token:
        try:
            data = jwt.decode(token, TOKEN_SECRET, algorithms=['HS256'])
            n = data.get('number')
            if n and len(n) is 11:
                data['number'] = normal_2_internal(n)
        except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError) as e:
            # return 403 to force re init
            if 'init' not in request.path:
                raise PermissionDenied()
    return data


def _get_user(request):
    """
    Returns the user model instance associated with the given request cookie.
    """
    data = request.token_data
    user_id = data.get('user_id')
    return user_id


def jwt_token_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request.token_data = SimpleLazyObject(lambda: _get_token(request))
        request.user_id = SimpleLazyObject(lambda: _get_user(request))

        request.update_token = {}
        response = get_response(request)

        if request.update_token:
            data = dict(request.token_data)
            data.update(request.update_token)
            v = jwt.encode(data, TOKEN_SECRET, algorithm='HS256')
            response.set_cookie("ctoken", v.decode())

        return response

    return middleware

