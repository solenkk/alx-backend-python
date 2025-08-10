import sqlite3
import functools

# In-memory query result cache
query_cache = {}

# Decorator to manage database connection
def with_db_connection(func):
    """Decorator to handle DB connection lifecycle."""
    @functools.wraps(func)
    def wrapper_with_connection(*args, **kwargs):
        conn = sqlite3.connect('users.db')  # Adjust path if needed
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper_with_connection

# Decorator to cache query results
def cache_query(func):
    """Cache query results to avoid redundant database calls."""
    @functools.wraps(func)
    def wrapper_cache(conn, query, *args, **kwargs):
        if query in query_cache:
            print("[Cache] Returning cached result")
            return query_cache[query]
        print("[DB] Executing and caching new query")
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper_cache

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call: hits the database and caches result
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call: uses cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")

# Optional: print to verify both results are identical
print(users == users_again)  # Should print: True
