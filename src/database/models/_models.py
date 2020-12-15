# ------------------ Imports ------------------
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

# ------------------ db Config ------------------
db = SQLAlchemy()
# ------------------ SQL classes  ------------------
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    person_id = db.Column(db.Integer(), db.ForeignKey("person.id"))
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f"Permission: {self.name}"
    
    
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    account = db.relationship("User", primaryjoin="and_(Person.id==User.person_id)")
    role = db.relationship("Role", backref='roles', primaryjoin="and_(Person.id==Role.person_id)")
    
    def __repr__(self):
        return f"Person({name})"
    
class User(db.Model, UserMixin):
    """
    User Model
    """
    id = db.Column("id", db.Integer, primary_key=True)
    person_id = db.Column(db.Integer(), db.ForeignKey("person.id"))
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100), unique=True)
    password = db.Column("password", db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
        
    def __repr__(self):
        return f"Name: {self.name}"
     
class Article(db.Model):
    """
    Article Model
    """
    __bind_key__ = 'articles'
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(100))
    author = db.Column("author", db.String(100))
    create_date = db.Column(db.String(100))
    short_desc = db.Column("short_description", db.String(150))
    title_img = db.Column(db.String(500))
    body = db.Column("body", db.String(900))