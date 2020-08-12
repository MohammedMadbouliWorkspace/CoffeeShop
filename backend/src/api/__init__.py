from flask import Flask, jsonify
from flask_cors import CORS

from .validation import *
from ..auth.auth import AuthError, requires_auth
from ..database.models import setup_db
from ..errors import default_message


def create_app(config_filename=None):
    app = Flask(__name__)

    try:
        app.config.from_pyfile(config_filename)
    except TypeError:
        pass

    setup_db(app)
    CORS(app)

    # !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    # !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
    # db_drop_and_create_all()

    # -------------------------------------------------------------#
    # Endpoints.
    # -------------------------------------------------------------#

    #  All drinks (in short format).
    #  ------------------------------------------------------------
    @app.route("/drinks", methods=['GET'])
    def get_drinks():
        """GET /drinks

        Fetches all drinks from the database.

        @parameters: No parameters needed.

        @headers: No headers needed.

        @return: (application/json) All drinks (short-formatted) in the database.

                - sample:
                {
                    "drinks": [
                        {
                            "id": 0,
                            "recipe": [
                                {
                                    "color": "#fff",
                                    "parts": 1
                                }
                            ],
                            "title": "foo"
                        },
                        ...
                    ]
                }
        """

        return jsonify(
            {
                "drinks": [
                    drink.short()
                    for drink
                    in Drink.get_all()  # Fetch all drinks
                ],
                "success": True
            }
        ), 200

    #  All drinks (in long format).
    #  ------------------------------------------------------------
    @app.route("/drinks-detail", methods=['GET'])
    @requires_auth(permission='get:drinks-detail')
    def get_drinks_detail(payload):
        """GET /drinks-detail

        Fetches all drinks from the database.

        @parameters: No parameters needed.

        @headers: 'Authorization' with a bearer token needed.

        @return: (application/json) All drinks (long-formatted) in the database.

                - sample:
                {
                    "drinks": [
                        {
                            "id": 0,
                            "recipe": [
                                {
                                    "color": "#fff",
                                    "name": "bar",
                                    "parts": 1
                                }
                            ],
                            "title": "foo"
                        },
                        ...
                    ]
                }
        """

        return jsonify(
            {
                "drinks": [
                    drink.long()
                    for drink
                    in Drink.get_all()  # Fetch all drinks
                ],
                "success": True
            }
        ), 200

    #  Add a drink.
    #  ------------------------------------------------------------
    @app.route("/drinks", methods=['POST'])
    @requires_auth(permission='post:drinks')
    @validate_json_data
    def post_drinks(data, payload):
        """POST /drinks

        Adds a drink record to the database.

        @parameters: No parameters needed.

        @headers: 'Authorization' with a bearer token needed.

        @body: (application/json) Required.

                - sample:
                {
                    "title": "tea",
                    "recipe": [
                        {
                            "color": "#44019B",
                            "name": "tea",
                            "parts": 1
                        },
                        ...
                    ]
                }

        @return: (application/json) The new drink (long-formatted).

                - sample:
                {
                    "drinks": [
                        {
                            "id": 1,
                            "recipe": [
                                {
                                    "color": "#44019B",
                                    "name": "tea",
                                    "parts": 1
                                }
                            ],
                            "title": "tea"
                        }
                    ]
                }
        """

        # Instantiate a new Drink model object
        drink = Drink()

        # Populate values to the model
        # Insert the model as a record to the database
        drink.add(
            title=validate_title(
                data.get("title"),
                request.method
            ),
            recipe=validate_recipe(
                data.get("recipe")
            )
        )

        return jsonify(
            {
                "drinks": [
                    drink.long()
                ],
                "success": True
            }
        ), 200

    #  Edit a drink.
    #  ------------------------------------------------------------
    @app.route("/drinks/<int:drink_id>", methods=['PATCH'])
    @requires_auth(permission='patch:drinks')
    @validate_json_data
    @check_drink
    def patch_drinks(drink, data, payload, drink_id):
        """PATCH /drinks/{drink_id}

        Selects a drink by its ID from '{drink_id}',
        and edits it in the database.

        @parameters: No parameters needed.

        @headers: 'Authorization' with a bearer token needed.

        @body: (application/json) Required.

                - sample: PATCH /drinks/1
                {
                    "title": "tea 2"
                }

        @return: (application/json) The edited drink (long-formatted).

                - sample:
                {
                    "drinks": [
                        {
                            "id": 1,
                            "recipe": [
                                {
                                    "color": "#44019B",
                                    "name": "tea",
                                    "parts": 1
                                }
                            ],
                            "title": "tea 2"
                        }
                    ]
                }
        """

        # Populate values to the model
        # Insert the model as a record to the database
        drink.add(
            title=validate_title(
                data.get("title") or drink.title,
                request.method, drink
            ),
            recipe=validate_recipe(
                data.get("recipe") or json.loads(drink.recipe)
            )
        )

        return jsonify(
            {
                "drinks": [
                    drink.long()
                ],
                "success": True
            }
        ), 200

    #  Delete a drink.
    #  ------------------------------------------------------------
    @app.route("/drinks/<int:drink_id>", methods=['DELETE'])
    @requires_auth(permission='delete:drinks')
    @check_drink
    def delete_drinks(drink, payload, drink_id):
        """DELETE /drinks/{drink_id}

        Selects a drink by its ID from '{drink_id}',
        and deletes it from the database.

        @parameters: No parameters needed.

        @headers: 'Authorization' with a bearer token needed.

        @body: No body needed.

        @return: (application/json) The deleted drink (long-formatted).

                - sample: DELETE /drinks/1
                {
                    "drinks": [
                        {
                            "id": 1,
                            "recipe": [
                                {
                                    "color": "#44019B",
                                    "name": "tea",
                                    "parts": 1
                                }
                            ],
                            "title": "tea 2"
                        }
                    ]
                }
        """

        # Cache the model object
        cache = {'drink': drink}

        # Delete the model as a record from the database
        drink.remove()

        return jsonify(
            {
                "drinks": [
                    cache['drink'].long()
                ],
                "success": True
            }
        ), 200

    # -------------------------------------------------------------#
    # Error Handlers.
    # -------------------------------------------------------------#

    @app.errorhandler(422)
    @default_message(DEF_UNPROCESSABLE)
    def unprocessable(description, code):

        return jsonify(
            {
                **{
                    "success": False,
                    "error": code,
                },
                **description
            }
        ), code

    @app.errorhandler(400)
    @default_message(DEF_BAD_REQUEST)
    def bad_request(description, code):

        return jsonify(
            {
                **{
                    "success": False,
                    "error": code,
                },
                **description
            }
        ), code

    @app.errorhandler(404)
    @default_message(DEF_NOT_FOUND)
    def not_found(description, code):

        return jsonify(
            {
                **{
                    "success": False,
                    "error": code,
                },
                **description
            }
        ), code

    @app.errorhandler(405)
    @default_message(DEF_METHOD_NOT_ALLOWED)
    def method_not_allowed(description, code):

        return jsonify(
            {
                **{
                    "success": False,
                    "error": code,
                },
                **description
            }
        ), code

    @app.errorhandler(AuthError)
    @default_message(DEF_UNAUTHORIZED)
    def failing_auth(description, code):

        return jsonify(
            {
                **{
                    "success": False,
                    "error": code,
                },
                **description
            }
        ), code

    @app.errorhandler(500)
    @default_message(DEF_INTERNAL_SERVER_ERROR)
    def internal_server_error(description, code):

        return jsonify(
            {
                **{
                    "success": False,
                    "error": code,
                },
                **description
            }
        ), code

    return app
