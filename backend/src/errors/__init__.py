from functools import wraps
from json import dumps


class ErrorDescription(dict):
    """A class for error description dictionary objects
    to be passed into 'abort' function or 'BaseException' object."""

    def __init__(self, description):
        super().__init__()
        # Set values from description param to 'ErrorDescription'
        for key, value in description.items():
            self[key] = value

    def __mod__(self, other):
        """Implement a string format to 'ErrorDescription' object.

        :param other: (seq) keywords to format with.
        :return: (dict) regular formatted dictionary.
        """
        return eval(dumps(self) % other)


class ErrorTemplate:
    """A class for error template objects
    to help generating string-formatted 'ErrorDescription' objects.
    """

    def __init__(self, description_template):
        self.description_template = description_template

    def g(self, *args):
        """Generates a string-formatted 'ErrorDescription' based on the template.

        :param args: (seq) keywords to format with.
        :return: (ErrorDescription) formatted ErrorDescription object.
        """
        return ErrorDescription(eval(dumps(self.description_template) % args))


def default_message(description=None):
    """A decorator for setting the default error description dictionary
    to 'Flask.error_handler'.

    :param description: (dict, ErrorDescription)
    :return: (func) decorated callback.
    """

    if description is None:
        description = {}

    def decorator(f):
        @wraps(f)
        def wrapper(error, *args, **kwargs):
            if type(error.description) == str:
                error.description = description

            return f(
                *args,
                description=error.description,
                code=error.code,
                **kwargs
            )

        return wrapper

    return decorator
