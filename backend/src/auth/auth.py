import json
from functools import wraps
from urllib.request import urlopen

from flask import request
from jose import jwt

from ..errors.messages import *

AUTH0_DOMAIN = 'wealwaystest.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'CoffeeShop'


class AuthError(Exception):
    """A standardized way to communicate auth failure modes."""

    def __init__(self, code=401, description=DEF_UNAUTHORIZED):
        self.code = code
        self.description = description


def get_token_auth_header():
    """Validates the Authentication header in the request,
    and returns the token if the validation passed.

    :return: (str) the token part of the header.
    """

    # Store the Authentication header as a list
    auth_header = [i for i in request.headers.get("Authorization", "").split(" ") if i]

    # Check for Authentication header existence
    if auth_header:

        # Check for Bearer token integrity
        if len(auth_header) == 2:

            # Check if the token starts with 'Bearer' prefix keyword
            if auth_header[0].lower() == "bearer":
                return auth_header[1]

            else:

                raise AuthError(400, AUTH_INVALID_PREFIX)

        else:

            raise AuthError(400, AUTH_INVALID_TOKEN)

    else:

        raise AuthError(401, AUTH_INVALID_HEADER)


def check_permissions(permission, payload):
    """Checks if a permission is included
    in the 'permissions' field in the 'payload' dictionary.

    :param permission: (str) The permission to be checked.
    :param payload: (dict) Payload helper dictionary to search in.
    :return: doesn't return a value but raises an 'AuthError' in failure state.
    """

    if permission not in payload.get("permissions"):

        raise AuthError


def verify_decode_jwt(token):
    """Verifies the truth of a JWT, and raises 'AuthError' in failure states.

    :param token: (bytes) The JWT as a bytes string.
    :return: (dict) The verified payload.
    """

    json_url = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')

    jwks = json.loads(json_url.read())

    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}

    if 'kid' not in unverified_header:

        raise AuthError(401, AUTH_MALFORMED)

    for key in jwks['keys']:

        if key['kid'] == unverified_header['kid']:

            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:

        try:

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:

            raise AuthError(401, AUTH_EXPIRED_TOKEN)

        except jwt.JWTClaimsError:

            raise AuthError(401, AUTH_INCORRECT_CLAIMS)

        except Exception:

            raise AuthError(400, AUTH_UNPARSABLE_TOKEN)

    raise AuthError(400, AUTH_INAPPROPRIATE_KEY)


def requires_auth(permission=''):
    """A decorator for running the Authorization implementations
    before fulfilling the request.

    :param permission: (str) The needed permission for the endpoint.
    :return: (func) decorated callback.
    """

    def requires_auth_decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):

            token = get_token_auth_header()

            payload = verify_decode_jwt(token)

            check_permissions(permission, payload)

            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
