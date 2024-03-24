# src/database/session.py
import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import streamlit as st

from AetherMind.database.base import Base  # Import your Base from models
from AetherMind.models import ( 
    # Import all of your models, so that they can be created all at once
    book,
)


# DATABASE_URL = f"postgresql://postgres.wggxwlhopitryatyprhk:{st.secrets['db_password']}@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
DATABASE_URL = st.secrets['db_url']

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def create_tables():
    try:
        # Set the default character set for the database
        with engine.connect() as connection:
            connection.execute(text("SET CHARACTER SET utf8mb4"))
            connection.execute(text("SET collation_connection = utf8mb4_unicode_ci"))
        
        table_args = {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci'
        }
        for table in Base.metadata.tables.values():
            table.kwargs.update(table_args)
            
        Base.metadata.create_all(bind=engine)
        print("Database tables created.")
    except OperationalError as e:
        print("Error occurred during Table creation!")
        print(e)

create_tables()

def get_session():
    return Session()

def check_db_connection():
    # Check connection
    try:
        db_session = Session()
        print("Checking database connection...")
        with engine.connect() as connection:
            print("Database connection established.")
            return True
    except OperationalError as e:
        print(e)
        print("Database connection could not be established.")
        return False
    finally:
        # Close the session
        db_session.close()
