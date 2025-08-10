import sqlite3
import functools
from datetime import datetime  

# Decorator to log SQL queries with timestamp
def log_queries(func):
    @functools.wraps(func)
    def wrapper_log(*args, **kwargs):
        query = kwargs.get('query') or (args[0] if args else None)
        if query:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Executing SQL Query: {query}")
        else:
            print("[LOG] No SQL query provided")
        return func(*args, **kwargs)
    return wrapper_log

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
print(users)
