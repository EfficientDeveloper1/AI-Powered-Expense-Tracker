from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Loading my environment variables
load_dotenv()

# I need to URL-encode the password because it contains special characters
password = quote_plus(os.getenv('DB_PASSWORD'))  # This handles the @ symbol in password

# Building my MySQL database URL from environment variables
# I'm using the format: mysql+pymysql://user:password@host:port/database
DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{password}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}"
)

# Creating my SQLAlchemy engine
# I'm using pool_pre_ping to test connections before using them
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # This checks if connection is still valid
    pool_size=10,        # I'll maintain 10 connections in the pool
    max_overflow=20      # Allowing up to 20 overflow connections
)

# Creating SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,  # I want to manually commit transactions
    autoflush=False,   # I'll control when to flush changes
    bind=engine        # Binding to my engine
)

# Creating base class that my models will inherit from
Base = declarative_base()

# Creating a dependency to get database session
def get_db():
    """
    I'm creating a new database session for each request.
    This yields the session and closes it after the request is done.
    I'll use this as a FastAPI dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()