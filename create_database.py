import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_finance_database():
    """Create the finance_tracker database in MySQL"""
    
    print("Creating the finance_tracker database...")
    
    try:
        # Connect to MySQL server using environment variables
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD')  # Now pulled from .env file
        )
        
        cursor = connection.cursor()
        
        # Create the database
        db_name = os.getenv('DB_NAME', 'finance_tracker')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created successfully!")
        
        # Show that it exists
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        print("\nAvailable databases:")
        for db in databases:
            if db[0] == db_name:
                print(f"  > {db[0]} (your expense tracker database)")
            else:
                print(f"  - {db[0]}")
            
        cursor.close()
        connection.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

if __name__ == "__main__":
    if create_finance_database():
        print("\nDatabase setup complete!")
    else:
        print("\nDatabase setup failed. Please check your MySQL credentials in .env file")