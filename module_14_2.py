import sqlite3

connection = sqlite3.connect('not_telegram.db')

cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users(
id INTEGER PRIMARY KEY,
username TEXT NOT NULL,
email TEXT NOT NULL,
age INTEGER,
balance INTEGER NOT NULL
)
''')

for i in range(10):
    cursor.execute('INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)',
                   (f'User{i+1}', f'example{i+1}@gmail.com', f'{(i+1)*10}', 1000))

cursor.execute('UPDATE Users SET balance = ? WHERE id % 2 = 1', (500,))

cursor.execute('DELETE FROM Users WHERE id % 3 = 1')

cursor.execute('DELETE FROM Users WHERE id = 6')

cursor.execute('SELECT COUNT(*) FROM Users')
count1 = cursor.fetchone()[0]
print(count1)

cursor.execute('SELECT SUM(balance) FROM Users')
sum1 = cursor.fetchone()[0]
print(sum1)

cursor.execute('SELECT AVG(balance) FROM Users')
avg1 = cursor.fetchone()[0]
print(avg1)

connection.commit()
connection.close()