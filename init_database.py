#!/usr/bin/env python3
"""
Initialize database tables using SQLAlchemy models
This ensures compatibility between our models and the actual database structure
"""
import os
from dotenv import load_dotenv
from model.models import db, User, Seller, Conversation, ChatReport
from model.config import DB_CONFIG
from flask import Flask

# Load environment variables first
load_dotenv('/home/marketing/elmachin/.env', override=True)

# Create Flask app
app = Flask(__name__)
app.config.update(DB_CONFIG)

# Debug: Print database URL to verify configuration
print(f"Database URL: {DB_CONFIG.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')}")

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    # Drop all tables first (clean slate)
    db.drop_all()
    print("Dropped existing tables")
    
    # Create all tables based on models
    db.create_all()
    print("Created all tables using SQLAlchemy models")
    
    # Add sample data
    try:
        # Create sample sellers
        sellers_data = [
            Seller(name='Carlos Rodriguez', email='carlos@gpscontrol.mx', phone='+525512345678', territory='Ciudad de Mexico'),
            Seller(name='Maria Gonzalez', email='maria@gpscontrol.mx', phone='+525587654321', territory='Guadalajara'),
            Seller(name='Juan Perez', email='juan@gpscontrol.mx', phone='+525599887766', territory='Monterrey')
        ]
        
        for seller in sellers_data:
            db.session.add(seller)
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@armaddia.lat',
            role='admin'
        )
        admin_user.set_password('admin123')  # Set a default password
        db.session.add(admin_user)
        
        # Commit all changes
        db.session.commit()
        print("Added sample data successfully")
        
        # Verify tables were created
        print("\nTables created:")
        with db.engine.connect() as connection:
            result = connection.execute(db.text("SHOW TABLES"))
            for row in result:
                print(f"- {row[0]}")
            
    except Exception as e:
        print(f"Error adding sample data: {e}")
        db.session.rollback()

print("\n✅ Database initialization complete!")