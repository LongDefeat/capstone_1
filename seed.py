from models import db
from app import app

# Create All Tables
db.drop_all()
db.create_all()