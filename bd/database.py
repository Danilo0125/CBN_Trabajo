import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sys
import os

# Add the parent directory to sys.path to allow absolute imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def get_database_uri():
    username = 'postgres'
    password = '12345678'
    host = 'localhost'
    port = '5432'
    # Fix database name - remove spaces and use a valid name
    database = 'Inteligencia2_Investigacion2'
    
    return f'postgresql://{username}:{password}@{host}:{port}/{database}'

def ensure_database_exists():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (to postgres database by default)
        conn = psycopg2.connect(
            user='postgres',
            password='12345678',
            host='localhost',
            port='5432',
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Use a valid database name without spaces
        db_name = 'Inteligencia2_Investigacion2'
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{db_name}'...")
            # Use the proper syntax for creating a database
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print("Database created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

def create_app():
    # First ensure the database exists
    ensure_database_exists()
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Import and initialize db with app
    from Modelos import db
    db.init_app(app)
    
    return app

def init_db(drop_all=False):
    """Initialize database and create all tables"""
    app = create_app()
    with app.app_context():
        from Modelos import db
        if drop_all:
            print("Eliminando todas las tablas existentes...")
            db.drop_all()
            print("Tablas eliminadas correctamente.")
        db.create_all()
        print("Base de datos inicializada correctamente. Tablas creadas.")
