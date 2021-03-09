# ------------------ Imports ------------------
from flask import jsonify
from flask_security import RoleMixin, SQLAlchemyUserDatastore
from flask_praetorian.user_mixins import SQLAlchemyUserMixin
from six import string_types
from ProjectsWebsite.modules import db

# ------------------ SQL classes  ------------------
class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.ForeignKey("user.id"))
    name = db.Column(db.String(80), unique=True)
    
    def __repr__(self):
        return f"{self.name}"
  
class User(db.Model, SQLAlchemyUserMixin):
    """
    User Model
    """
    __tablename__ = 'user'
    role_model = Role()
    
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    username = db.Column("username", db.String(100), unique=True)
    hashed_password = db.Column("hashed_password", db.String(255))
    is_active = db.Column("is_active", db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    created_at = db.Column("date", db.String(30))
    blacklisted = db.Column(db.Boolean())
    roles = db.relationship('Role', primaryjoin="and_(User.id==Role.user_id)",
                            backref=db.backref('users'))
    
    def _put(self, model):
        db.session.add(model)
        return model
    
    def _prepare_user_and_role_args(self, user, role):
        if isinstance(user, string_types):
            user = self.lookup(user)
        if isinstance(role, string_types):
            role = self.find_role(self, role)
        return user, role
    
    def _prepare_user_account(self, **kwargs):
        kwargs.setdefault('is_active', True)
        roles = kwargs.get('roles', [])
        for i, role in enumerate(roles):
            rn = role.name if isinstance(role, type(self.role_model)) else role
            roles[i] = self.find_role(self, rn)
        kwargs['roles'] = roles
        return kwargs
    
    @classmethod    
    def create_user(cls, **kwargs):
        """
        creates new user in the users sql database
        """
        kwargs = cls._prepare_user_account(cls, **kwargs)
        user = cls(**kwargs)
        return cls._put(cls, user)
    
    def add_role(self, user, role):
        """
        Adds role to specified user
        """
        added = False
        user, role = self._prepare_user_and_role_args(self, user, role)
        if role not in user.roles:
            added = True
            user.roles.append(role)
        self._put(self, user)
        return added
    
    def remove_role(self, user, role):
        """
        Remove role from specified user
        """
        removed = False
        user, role = self._prepare_user_and_role_args(self, user, role)
        if role in user.roles:
            removed = True
            user.roles.remove(role)
        self._put(self, user)
        return removed
    
    def find_role(self, role):
        """
        finds role specified
        """
        return self.role_model.query.filter_by(name=role).first()
    
    def delete_user(self, user):
        """
        Deletes Specified User
        """
        db.session.delete(user)
       
    def get_id(self):
        """
        for Flask-Login
        """
        return self.identity
    
    def to_json(self):
        return jsonify(
                       email=self.username,
                       password=self.hashed_password)
        
    def __repr__(self):
        return self.name

class Article(db.Model):
    """
    Article Model
    """
    __tablename__ = 'article'
    __bind_key__ = 'articles'
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(100))
    author = db.Column("author", db.String(100))
    create_date = db.Column(db.String(100))
    short_desc = db.Column("short_description", db.String(150))
    title_img = db.Column(db.String(500))
    body = db.Column("body", db.String(900))
    
    
class Blacklist(db.Model):
    """
    Blacklist Model
    """
    __tablename__ = 'blacklist'
    __bind_key__ = 'blacklist'
    id = db.Column("id", db.Integer(), primary_key=True)
    blacklisted_person = db.Column("person", db.String(100), unique=True, nullable=False)
    date_blacklisted = db.Column("date", db.String(30))
    
    

# ------------------ datastore  ------------------
user_datastore = SQLAlchemyUserDatastore(db, User, Role)