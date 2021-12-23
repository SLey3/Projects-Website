# ------------------ Imports ------------------
from typing import List

from flask_security import SQLAlchemyUserDatastore
from sqlalchemy import text

from ProjectsWebsite.modules import db
from ProjectsWebsite.util import AnonymousUserMixin, DateUtil, RoleMixin, UserMixin

# ------------------ SQL classes  ------------------
dt = DateUtil(format_token="L LTS zzZ z")


class Role(db.Model, RoleMixin):
    """
    Role model for all roles in this website
    """

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f"{self.name}"


class User(db.Model, UserMixin):
    """
    User Model for all users with accounts
    """

    __tablename__ = "user"

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))
    username = db.Column("username", db.String(100), unique=True)
    hashed_password = db.Column("hashed_password", db.String(255))
    user_salt = db.Column(db.String, unique=True)
    active = db.Column("active", db.Boolean)
    created_at = db.Column("date", db.String(30))
    blacklisted = db.Column(db.Boolean)
    roles = db.relationship(
        "Role",
        backref=db.backref("users", lazy="subquery"),
        primaryjoin="and_(User.id==Role.user_id)",
    )


class AnonymousUser(AnonymousUserMixin):
    """
    AnonymousUser class for not logged in users
    """

    ...


class Article(db.Model):
    """
    Article Model for all articles
    """

    __tablename__ = "article"

    __bind_key__ = "articles"

    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(100))
    author = db.Column("author", db.String(100))
    create_date = db.Column(db.String(100))
    short_desc = db.Column("short_description", db.String)
    title_img = db.Column(db.String)
    body = db.Column("body", db.String)
    download_pdf = db.Column(db.LargeBinary)

    @classmethod
    def delete(cls, id):
        """
        delete an article by id
        """
        return cls.query.filter(cls.id == id).delete()

    @classmethod
    def delete_all(cls, author):
        """
        Delete all of a specific authors article
        """
        return cls.query.filter(cls.author == author).delete()


class Blacklist(db.Model):
    """
    Blacklist Model
    """

    __tablename__ = "blacklist"

    __bind_key__ = "blacklist"

    id = db.Column("id", db.Integer(), primary_key=True)
    name = db.Column("person", db.String(100), unique=True, nullable=False)
    reason = db.Column("reason", db.String(255))
    date_blacklisted = db.Column("date", db.String(30))

    @classmethod
    def add_blacklist(cls, **kwargs):
        """
        adds a person to the Blacklist database (e.g. Ban)
        """
        date = dt.subDate()
        kwargs.setdefault("date_blacklisted", date)
        return cls(**kwargs)

    @classmethod
    def remove_blacklist(cls, name):
        """
        removes a person from the Blacklist database (e.g. UnBan)
        """
        return cls.query.filter(cls.name == name).delete()


# ------------------ user_datastore  ------------------
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

# ------------------ User Initialization Function ------------------
def initialize_user(roles: List[str], **kwargs):
    """
    Creates and adds role's to specified user and commits the changes
    """

    def _add_roles(user, *roles):
        for role in roles:
            user_datastore.add_role_to_user(user, Role(name=role))
        User.commit()

    user = kwargs.get("name")
    user_datastore.create_user(**kwargs)
    User.commit()
    user = User.lookup_by_name(user)
    _add_roles(user, *roles)
