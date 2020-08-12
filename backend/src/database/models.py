import os
from sqlalchemy import Column, String, Integer
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import abort
import json

from ..errors.messages import DEF_UNPROCESSABLE

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()


class DBActionsExceptionsHandler:

    def __init__(self, session):
        self.session = session

    def fetch(self, origin):

        def wrapper(cls, **kwargs):
            try:
                data = origin(cls, **kwargs)
                return data

            except SQLAlchemyError:
                self.session.close()
                abort(500, DEF_UNPROCESSABLE)

        return wrapper

    def change(self, origin):

        def wrapper(cls, **kwargs):

            try:
                origin(cls, **kwargs)
                self.session.commit()
                return True

            except SQLAlchemyError:
                self.session.rollback()
                self.session.close()
                abort(500, DEF_UNPROCESSABLE)

        return wrapper


class DBActions:
    exception_handler = DBActionsExceptionsHandler(db.session)

    session = exception_handler.session

    @classmethod
    @exception_handler.fetch
    def get_one(cls, id):
        return cls.session.query(cls).filter(cls.id == id).first()

    @classmethod
    @exception_handler.fetch
    def get_all(cls, loadonly=None):
        if loadonly:
            return cls.query.options(loadonly).all()

        return cls.session.query(cls).all()

    @classmethod
    @exception_handler.fetch
    def get_filtered(cls, filter=True):
        return cls.query.filter(filter).first()

    @exception_handler.change
    def add(self, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.session.add(self)

    @exception_handler.change
    def remove(self):
        self.session.delete(self)


def setup_db(app):
    """Binds a flask application and a SQLAlchemy service"""

    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def db_drop_and_create_all():
    """Drops the database tables and starts fresh,
    and can be used to initialize a clean database."""

    db.drop_all()
    db.create_all()


class Drink(db.Model, DBActions):
    """A persistent drink entity, extends the base SQLAlchemy Model."""

    # Autoincrement, unique primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)

    # String Title
    title = Column(String(80), unique=True)

    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    recipe = Column(String(180), nullable=False)

    def short(self):
        """Short form representation of the Drink model."""
        short_recipe = [{'color': r['color'], 'parts': r['parts']} for r in json.loads(self.recipe)]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }

    def long(self):
        """Long form representation of the Drink model."""

        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }

    def __repr__(self):
        return json.dumps(self.short())
