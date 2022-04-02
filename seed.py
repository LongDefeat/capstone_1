from models import db, bcrypt
from app import app

# Create All Tables
db.drop_all()
db.create_all()