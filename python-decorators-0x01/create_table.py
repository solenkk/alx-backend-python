import csv
import sqlite3

def read_csv_data(filename):
    data = []
    with open(filename, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append({
                'name': row['name'],
                'email': row['email'],
                'age': row['age']
            })
    return data

def insert_data(connection, filename):
    data = read_csv_data(filename)
    for line in data:
        try:
            with connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT email FROM users WHERE email=?", (line['email'],))
                if cursor.fetchone():
                    print(f"User with email {line['email']} already exists. Skipping.")
                    continue  # Use continue, not return, to process all rows

                query = """
                    INSERT INTO users(name, email, age)
                    VALUES (?, ?, ?)
                """
                cursor.execute(
                    query,
                    (line['name'], line['email'], line['age'])
                )
        except sqlite3.OperationalError as err:
            print(f"Error inserting data: {err}")

if __name__ == '__main__':
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            age INTEGER NOT NULL
        )
    """)
    insert_data(con, 'user_data.csv')
    con.commit()
    con.close()
