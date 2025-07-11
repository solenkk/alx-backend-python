import sqlite3
import functools

# Decorator: handles opening and closing the DB connection
def with_db_connection(func):
    """Decorator to manage DB connection lifecycle."""
    @functools.wraps(func)
    def wrapper_with_connection(*args, **kwargs):
        conn = sqlite3.connect('users.db')  # Replace with your DB path if needed
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper_with_connection

# Decorator: handles transaction management (commit/rollback)
def transactional(func):
    """Decorator to manage DB transactions."""
    @functools.wraps(func)
    def wrapper_transaction(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            print(f"Transaction rolled back due to: {e}")
            raise
    return wrapper_transaction

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))

# Example usage
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
