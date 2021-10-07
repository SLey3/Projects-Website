# ------------------ Imports ------------------

from flask_praetorian.user_mixins import SQLAlchemyUserMixin
from flask_security import SQLAlchemyUserDatastore

from ProjectsWebsite import modules

try:
    from ProjectsWebsite.database.models.roles import Roles
    from ProjectsWebsite.modules import db
    from ProjectsWebsite.util import AnonymousUserMixin, DateUtil, RoleMixin
except ModuleNotFoundError:
    from ...modules import db
    from ...util import AnonymousUserMixin, DateUtil, RoleMixin
    from .roles import Roles

# ------------------ SQL classes  ------------------
dt = DateUtil(format_token="L LTS zzZ z")


class Role(db.Model, RoleMixin):
    """
    Role model for all roles in this website
    """

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.Enum(Roles), unique=True)

    def __repr__(self):
        return f"{self.name}"


class User(db.Model, SQLAlchemyUserMixin):
    """
    User Model for all users with accounts
    """

    __tablename__ = "user"

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))
    username = db.Column("username", db.String(100), unique=True)
    hashed_password = db.Column("hashed_password", db.String(255))
    active = db.Column("active", db.Boolean)
    created_at = db.Column("date", db.String(30))
    blacklisted = db.Column(db.Boolean)
    roles = db.relationship(
        "Role",
        backref=db.backref("users", lazy="subquery"),
        primaryjoin="and_(User.id==Role.user_id)",
    )

    def has_role(self, role):
        """
        Checks if role is in the users role
        """
        return role in self.roles

    @classmethod
    def lookup_by_name(cls, name):
        """
        looks up user by name
        """
        return cls.query.filter_by(name=name).one_or_none()

    @classmethod
    def activate(cls, email):
        """
        Activates user
        """
        user = cls.lookup(email)
        if user.active:
            return False
        else:
            user.active = True
            db.session.add(user)
            db.session.commit()
            return True

    @classmethod
    def deactivate(cls, email):
        """
        deactivates user
        """
        user = cls.lookup(email)
        if user.active:
            user.active = False
            db.session.add(user)
            db.session.commit()
            return True
        return False

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        """
        for Flask-Login
        """
        return self.identity

    def verify_password(self, hashed_pwd):
        """
        Returns True if hashed_pwd equals the users password
        """
        return hashed_pwd == self.hashed_password

    @property
    def is_authenticated(self):
        """
        returns if user is authenticated
        """
        return True

    @property
    def is_blacklisted(self):
        """
        returns if user is blacklisted
        """
        if self.blacklisted:
            return True
        return False

    def iter_roles(self):
        for role in self.roles:
            current_name = str(role.name.value).replace("<", "").replace(">", "")
            role.name = current_name.capitalize()
            yield role

    def __repr__(self):
        return self.name


class AnonymousUser(AnonymousUserMixin):
    """
    AnonymousUser class for not logged in users
    """


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
