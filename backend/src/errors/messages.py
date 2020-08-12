from . import ErrorTemplate

# Default error template
e = ErrorTemplate(
    {
        "message": "%s"
    }
)

# Default error descriptions for common HTTP errors
DEF_UNPROCESSABLE = e.g("The operation has failed.")
DEF_BAD_REQUEST = e.g("The request is malformed or needs some modifications.")
DEF_NOT_FOUND = e.g("The resource was not found.")
DEF_METHOD_NOT_ALLOWED = e.g("This method is not permitted at this endpoint.")
DEF_UNAUTHORIZED = e.g("You are not authorized as your credentials are invalid.")
DEF_INTERNAL_SERVER_ERROR = e.g("Sorry, the server ran into a problem.")

# Error descriptions for drink-related validations at the endpoints
DRINK_UNUSABLE_TITLE = e.g("This title '%s' is already in use.")
DRINK_INVALID_RECIPE_JSON_ARRAY = e.g("The recipe must be a JSON Array of ingredient objects.")
DRINK_INVALID_RECIPE_INGREDIENT_OBJECTS = e.g("Some ingredient objects have problems "
                                              "can be fixed by looking at 'debug' array.")
DRINK_INVALID_RECIPE_INGREDIENT_OBJECT = e.g("The ingredient of indices [%s] must be JSON objects.")
DRINK_INVALID_JSON_DATA = e.g("The JSON data is malformed. %s.")
DRINK_NOT_FOUND = e.g("The drink was not found.")

# Error descriptions for authentication validations at the endpoints
AUTH_INVALID_PREFIX = e.g("Authorization header must start with 'Bearer'.")
AUTH_INVALID_TOKEN = e.g("Authorization header must be bearer token.")
AUTH_INVALID_HEADER = e.g("Authorization header is expected.")
AUTH_MALFORMED = e.g("Authorization malformed.")
AUTH_EXPIRED_TOKEN = e.g("Token expired.")
AUTH_INCORRECT_CLAIMS = e.g("Incorrect claims. Please, check the audience and issuer.")
AUTH_UNPARSABLE_TOKEN = e.g("Unable to parse authentication token.")
AUTH_INAPPROPRIATE_KEY = e.g("Unable to find the appropriate key.")