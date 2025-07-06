import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ALX_prodev"
    )
def stream_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")
    
    while True:
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            break yield row
