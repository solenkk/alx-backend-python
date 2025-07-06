import mysql.connector
import csv
import uuid

def connect_db():
    """Connect to the MySQL server"""
    try:
        connection = mysql.connector.connect(
      host="localhost",
       user="root",  
           password=""   
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def create_database(connection):
    """Create ALX_prodev database if it doesn't exist"""
    try:
     cursor = connection.cursor()
      cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
      print("Database ALX_prodev created successfully")
   cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")

def connect_to_prodev():
    """Connect to the ALX_prodev database"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  
            password="",   
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev: {err}")
        return None

def create_table(connection):
    """Create user_data table if it doesn't exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(10,0) NOT NULL,
                INDEX (user_id)
            )
        """)
        print("Table user_data created successfully")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")

def insert_data(connection, csv_file):
    """Insert data from CSV file into user_data table"""
    try:
        cursor = connection.cursor()
        
        with open(csv_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
              
                cursor.execute("SELECT * FROM user_data WHERE user_id = %s", (row['user_id'],))
                if cursor.fetchone() is None:
                    cursor.execute("""
                        INSERT INTO user_data (user_id, name, email, age)
                        VALUES (%s, %s, %s, %s)
                    """, (row['user_id'], row['name'], row['email'], row['age']))
        
        connection.commit()
        print("Data inserted successfully")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
    except FileNotFoundError:
        print(f"Error: CSV file {csv_file} not found")
    except Exception as e:
        print(f"Unexpected error: {e}")
