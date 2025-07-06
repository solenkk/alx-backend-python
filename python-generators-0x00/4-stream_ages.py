import seed

def stream_user_ages():
    connection = seed.connect_to_prodev()
    cursor = connection.cursor()
    cursor.execute("SELECT age FROM user_data")
    
    while True:
        row = cursor.fetchone()
        if not row:
            cursor.close()
            connection.close()
            break
        yield row[0]

def calculate_average_age():
    total = 0
    count = 0
    
    for age in stream_user_ages():
        total += age
        count += 1
    
    if count > 0:
        average = total / count
        print(f"Average age of users: {average:.2f}")
    else:
        print("No users found")

if __name__ == "__main__":
    calculate_average_age()
