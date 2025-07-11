import sqlite3
import functools

def with_db_connection(func):
    """Decorator to open and close a database connection around a function call."""
    @functools.wraps(func)
    def wrapper_with_connection(*args, **kwargs):
        # Open the database connection
        conn = sqlite3.connect('users.db')  # Replace with your actual DB name/path
        try:
            # Pass the connection to the decorated function
            result = func(conn, *args, **kwargs)
        finally:
            # Always close the connection after use
            conn.close()
        return result
    return wrapper_with_connection

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Fetch user by ID with automatic connection handling
user = get_user_by_id(user_id=1)
print(user)
