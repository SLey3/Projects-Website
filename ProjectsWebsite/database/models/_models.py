# ------------------ Imports ------------------
from flask_security import UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ------------------ SQL classes  ------------------
class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.ForeignKey("user.id"))
    name = db.Column(db.String(80), unique=True)
    
    def __repr__(self):
        return f"{self.name}"
  
class User(db.Model, UserMixin):
    """
    User Model
    """
    __tablename__ = 'user'
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100), unique=True)
    password = db.Column("password", db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    created_at = db.Column("date", db.String(30))
    blacklisted = db.Column(db.Boolean())
    roles = db.relationship('Role', primaryjoin="and_(User.id==Role.user_id)",
                            backref=db.backref('users'))
        
    def to_json(self):
        data = {
            "email": self.email,
            "pwd": self.password
        } 
        return data
        
    def __repr__(self):
        return f"{self.name}"
     
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