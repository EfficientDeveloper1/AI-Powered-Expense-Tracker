from app.core.database import engine, Base
from app.models.models import User, Expense, Budget  # Importing my models to register them
import mysql.connector
from dotenv import load_dotenv
import os

# Loading environment variables
load_dotenv()

def init_database():
    """
    I'm creating all the tables in my database based on the models I've defined.
    This will only create tables that don't exist yet.
    """
    
    print("Starting database initialization...")
    
    try:
        # First, I'll make sure the database exists
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD')
        )
        cursor = connection.cursor()
        
        # Creating database if it doesn't exist
        db_name = os.getenv('DB_NAME', 'finance_tracker')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' is ready")
        
        cursor.close()
        connection.close()
        
        # Now I'll create all tables using SQLAlchemy
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully!")
        
        # Let me check what tables were created
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD'),
            database=db_name
        )
        cursor = connection.cursor()
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("\nTables in database:")
        for table in tables:
            print(f"  - {table[0]}")
            
        # I'll also show the structure of each table
        for table in tables:
            print(f"\nStructure of {table[0]}:")
            cursor.execute(f"DESCRIBE {table[0]}")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  - {column[0]}: {column[1]}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    if init_database():
        print("\nDatabase initialization complete! Your tables are ready.")
    else:
        print("\nDatabase initialization failed. Please check the error above.")