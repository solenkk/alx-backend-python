import time
import sqlite3
import functools

# Decorator to manage DB connection
def with_db_connection(func):
    """Decorator to handle DB connection lifecycle."""
    @functools.wraps(func)
    def wrapper_with_connection(*args, **kwargs):
        conn = sqlite3.connect('users.db')  # Update path if needed
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper_with_connection

# Decorator to retry failed DB operations
def retry_on_failure(retries=3, delay=2):
    """Retry decorator with customizable retries and delay."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Attempt {attempts} failed: {e}")
                    if attempts < retries:
                        time.sleep(delay)
                    else:
                        print("All retry attempts failed.")
                        raise
        return wrapper_retry
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Run and print results
users = fetch_users_with_retry()
print(users)
