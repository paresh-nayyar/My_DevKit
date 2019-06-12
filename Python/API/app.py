import io
import json
import re
import socket
import sqlite3

import cv2
import numpy as np
from flask import Flask, render_template
from flask import request, jsonify, Response
from keras.models import model_from_json

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

with open('books.json') as file:
    books = json.load(file)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route("/template/<user>")
def display_name(user):
    return render_template('hello.html', name=user)


@app.route("/template")
def display_name1():
    query_parameters = request.args
    user = query_parameters.get('name')
    return render_template('hello.html', name=user)


@app.route("/", methods=['GET'])
def home():
    return '<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science ' \
           'fiction novels.</p>'


@app.route('/books/all', methods=['GET'])
def api_all():
    return (jsonify(books))


@app.route('/books', methods=['GET'])
def api_id():
    if 'id' in request.args:
        id = int(request.args['id'])
        print(request.args)
    else:
        return "Error: No id field provided. Please specify an id"

    results = []

    for k, v in books.items():
        if (books.get(k).get('id') == id):
            results.append(books.get(k))

    return jsonify(results)


@app.route('/books/db/all', methods=['GET'])
def api_all_db():
    conn = sqlite3.connect('books.db')
    cur = conn.cursor()
    all_books = cur.execute('SELECT * FROM books;').fetchall()
    conn.close()
    return jsonify(all_books)


@app.route('/books/db', methods=['GET'])
def api_filter_db():
    query_parameters = request.args
    id = (query_parameters.get('id'))
    published = (query_parameters.get('published'))
    author = query_parameters.get('author')

    query = 'SELECT * FROM books WHERE'
    to_filter = []

    if id:
        query = query + ' id=? AND'
        to_filter.append(int(id))

    if published:
        query = query + ' published=? AND'
        to_filter.append(int(published))

    if author:
        query = query + ' author=? AND'
        to_filter.append(author)

    if (not (id or published or author)):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('books.db')
    cur = conn.cursor()
    results = cur.execute(query, to_filter).fetchall()
    conn.close()
    return jsonify(results)


@app.route('/books/add', methods=['POST'])
def add_entry():
    receive = request.get_json()
    new_book = {
        'id': receive.get('id'),
        'title': receive.get('title'),
        'author': receive.get('author'),
        'published': receive.get('published')
    }

    get_key = list(books.keys())[-1]
    new_record = 'Item' + str(int(re.findall("[0-9]+", get_key)[0]) + 1)

    books[new_record] = new_book

    with open('books.json', 'w') as outfile:
        json.dump(books, outfile, indent=True)

    return jsonify({'test': new_book}), 201


@app.route('/books/db/add', methods=['POST'])
def add_record_db():
    receive = request.form
    id = receive.get('id')
    title = receive.get('title')
    author = receive.get('author')
    published = receive.get('published')
    first_sentence = receive.get('first_sentence')

    to_add = [int(id), title, author, int(published), first_sentence]
    query = 'INSERT INTO books (id, title, author, published, first_sentence) VALUES(?,?,?,?,?);'

    conn = sqlite3.connect('books.db')
    cur = conn.cursor()
    cur.execute(query, to_add)
    conn.commit()
    conn.close()
    return Response(status=200, mimetype="application/json")


@app.route('/test_file', methods=['POST'])
def test_file():
    # load json and create model
    with open('model_cats_dogs.json', 'r') as read_model:
        model_file = read_model.read()
        read_model.close()

    loaded_model = model_from_json(model_file)

    # load weights into new model
    loaded_model.load_weights("model_cats_dogs.h5")
    print("Loaded model from disk")

    loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    if (request.data):
        receive = request.data
        getdata = np.fromstring(receive, np.uint8)
        img = cv2.imdecode(getdata, cv2.IMREAD_COLOR)
        cv2.imwrite('test.png', img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = img / 255
        test_image = cv2.resize(img, (150, 150))
        test_image = np.array(test_image).reshape(-1, 150, 150, 1)
        pred = int(loaded_model.predict_classes(test_image))
        category = 'Cat' if pred == 1 else 'Dog'
        return 'This is a {}'.format(category)

    elif (request.files):

        image = request.files['file']
        in_memory_file = io.BytesIO()
        image.save(in_memory_file)
        data = np.fromstring(in_memory_file.getvalue(), dtype=np.uint8)
        img = cv2.imdecode(data, 1)
        cv2.imwrite('test.png', img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = img / 255

        test_image = cv2.resize(img, (150, 150))
        test_image = np.array(test_image).reshape(-1, 150, 150, 1)
        pred = int(loaded_model.predict_classes(test_image))
        category = 'Cat' if pred == 1 else 'Dog'
        return 'This is a {}'.format(category)

    else:
        return 'File format not supported'


if __name__ == '__main__':
    print(__name__)
    hostname = socket.gethostname()
    address = socket.gethostbyname(hostname)
    app.run(host=address, port=5000, debug=True)
