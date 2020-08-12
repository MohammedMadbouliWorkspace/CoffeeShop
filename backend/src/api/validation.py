import re
import json
from json.decoder import JSONDecodeError
from flask import abort, request
from functools import wraps
from ..database.models import Drink
from ..errors.messages import *


def validate_title(title, method, for_patch=None):
    """Validates the usage of a title,
    raises 422 Error if title is already in use,
    and ignores raising errors if title is already in use
    but used by the same modified drink.

    :param title: (str) The title to validate.
    :param method: (str) ['POST', 'PATCH'] A helper for the title check.
    :param for_patch: (object) [only in method='PATCH'] The drink object that needs to be modified.
    :return: (str) The valid title.
    """

    drink = Drink.get_filtered(filter=Drink.title == title)

    if method == 'POST':

        #
        if drink:
            abort(422, DRINK_UNUSABLE_TITLE % title)

        else:
            return title

    elif method == 'PATCH':

        #
        if drink and drink != for_patch:
            abort(422, DRINK_UNUSABLE_TITLE % title)

        else:
            return title


def validate_recipe(recipe_raw):
    """Detects any issues in the recipe dictionary.

    :param recipe_raw: (dict) The recipe dictionary to validate.
    :return: (JSONEncoder) The recipe JSON data.
    """

    # Check if recipe is a list
    if type(recipe_raw) != list:
        abort(400, DRINK_INVALID_RECIPE_JSON_ARRAY)

    # Store [i]ngredient [v]alidation [c]ollection
    ivc = [
        (
            "color",
            lambda v: re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", v),
            lambda v: f"The 'color' should be a hexadecimal, "
                      f"for e.g., #000, #ffffff (not '{v}')."
        ),
        (
            "name",
            lambda v: True, lambda v: ""
        ),
        (
            "parts", lambda v: int(v) or 1 if str(v).isdigit() else False,
            lambda v: f"The 'parts' should be a number (not '{type(v).__name__}')."
        )
    ]

    # Detect issues on recipe level and ingredient level
    failure_points = list(
        filter(
            lambda p: p["reasons"],
            [
                {
                    "index": i,
                    "reasons":
                        list(
                            filter(
                                None,
                                [
                                    f"Key '{key}' is missing."
                                    if key not in recipe_raw[i].keys()
                                    else error_message(recipe_raw[i][key])
                                    if not validator(recipe_raw[i][key])
                                    else None
                                    for key, validator, error_message
                                    in ivc  # ingredient level
                                ]
                            )
                        )
                }
                if type(recipe_raw[i]) == dict
                else {
                    "index": i,
                    "reasons": ["The ingredient must be a JSON object."]
                }
                for i in range(len(recipe_raw))  # recipe level
            ]
        )
    )

    if failure_points:

        abort(
            400,
            {
                **DRINK_INVALID_RECIPE_INGREDIENT_OBJECTS,
                **{"debug": failure_points}
            }
        )

    else:

        return json.dumps(recipe_raw)


def validate_json_data(f):
    """A decorator for validating provided JSON data in the request body.

    :return: (func) decorated callback.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):

        try:

            data = json.loads(request.data)

            return f(
                data,
                *args,
                **kwargs
            )

        except JSONDecodeError as exception:

            abort(400, DRINK_INVALID_JSON_DATA % exception)

    return wrapper


def check_drink(f):
    """A decorator for checking the existence of a drink.

    :return: (func) decorated callback.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):

        drink = Drink.get_one(id=kwargs.get("drink_id"))

        if drink:

            return f(
                drink,
                *args,
                **kwargs
            )

        else:

            abort(404, DRINK_NOT_FOUND)

    return wrapper
