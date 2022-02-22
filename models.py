"""SQLAlchemy models for Users and Favorites - Cocktail DB."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(db.Text, 
                nullable=False,
                unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    last_name = db.Column(
        db.Text,
        nullable=False,
    )
    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    bio = db.Column(
        db.Text,
    )

    favorites = db.relationship('Favorite', backref='users')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, first_name, last_name):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Favorite(db.Model):
    """User Favorite Recipes"""
    
    __tablename__ = 'favorites'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
    )

    drink_id = db.Column(
        db.Integer, 
        nullable=False,
    )

    @classmethod
    def save_drink(cls, user_id, drink_id):
        drink = Favorite(
            user_id=user_id,
            drink_id = drink_id
        )
        db.session.add(drink)
        db.session.commit()
        return drink

class Cocktail(db.Model):
    """Searched Cocktails"""
    __tablename__ = 'cocktails'

    id=db.Column(
                db.Integer, 
                primary_key=True,
                nullable=False,
    )

    drink_id = db.Column(
                db.Integer, 
                primary_key=True,
                nullable=False,
    )
    cocktail_data = db.Column(
                    db.Text,
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.user_id}, {self.drink_id}>"

    @classmethod
    def add_drink(cls, drink_id, cocktail_data):
        """Add Cocktail to DB.
        """

        cocktail = Cocktail(
            drink_id=drink_id,
            cocktail_data=cocktail_data,
        )

        db.session.add(cocktail)
        db.session.commit()
        return cocktail


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

