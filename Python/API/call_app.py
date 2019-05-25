# Calling the server in app.py
import requests
import sqlite3
import pandas as pd
import socket
import cv2

hostname = socket.gethostname()
address = socket.gethostbyname(hostname)
port = 5000
# fetch book data
req1 = requests.get('http://{}:{}'.format(address, port))
req2 = requests.get('http://{}:{}/books/all'.format(address, port)).json()
req3 = requests.get('http://{}:{}/books/db/all'.format(address, port)).json()
req4 = requests.get('http://{}:{}/books'.format(address, port), params={'id': 0}).json()
req5 = requests.get('http://{}:{}/books/db'.format(address, port),
                    params={'published': 1993, 'author': 'Vernor Vinge'}).json()

# post data
req6 = requests.post('http://{}:{}/books/add'.format(address, port),
                     json={'id': 100, 'title': 'A Game of Thrones', 'author': 'George RR Martin',
                           'published': 1996})
req7 = requests.post('http://{}:{}/books/add'.format(address, port),
                     json={'id': 101, 'title': 'A Clash of Kings', 'author': 'George RR Martin',
                           'published': 1998})
req8 = requests.post('http://{}:{}/books/add'.format(address, port),
                     json={'id': 102, 'title': 'A Storm of Swords', 'author': 'George RR Martin',
                           'published': 2000})


req8 = requests.post('http://{}:{}/books/db/add'.format(address, port),
                     data={'id': 110, 'title': 'A Game of Thrones', 'author': 'George RR Martin',
                           'published': 1996})

req9 = requests.post('http://{}:{}/books/db/add'.format(address, port),
                     data={'id': 6009, 'title': 'A Clash of Kings test', 'author': 'George RR Martin',
                           'published': 1998})

# Sending image
img = cv2.imread('../Image Classification/PetImages/Dog/0.jpg')
_, img_encoded = cv2.imencode('.jpg', img)
content_type = 'image/jpeg'
headers = {'Content-type': content_type}
req10 = requests.post('http://{}:{}/test_file'.format(address, port), data=img_encoded.tostring(), headers=headers)

# Connecting to DB
conn = sqlite3.connect('books.db')
cur = conn.cursor()
df = pd.DataFrame(cur.execute('SELECT * FROM books').fetchall(),
                  columns=['id', 'pubished', 'author', 'title', 'first_sentence'])

df['id'] = range(1001, (1001+df.shape[0]))
cur.execute("DROP TABLE books;")
conn.commit()
df.to_sql('books', conn, index=False)
conn.commit()

# Adding a new table
cur.execute("CREATE TABLE person(id INTEGER PRIMARY KEY,\
                                 first_name TEXT,\
                                 last_name TEXT,\
                                 age INTEGER);")

cur.execute("INSERT INTO person\
             VALUES (101, 'Chris', 'Hemsworth',35); ")

df2 = pd.DataFrame(cur.execute('SELECT * FROM person').fetchall(),
                  columns=['id', 'first_name', 'last_name', 'age'])

cur.execute("ALTER TABLE books DROP COLUMN id;")
cur.execute("DELETE FROM books WHERE id = 110;")
conn.commit()
cur.close()
conn.close()
