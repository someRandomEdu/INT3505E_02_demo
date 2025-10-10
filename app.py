import apiflask
import marshmallow.fields
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from apiflask import APIFlask, Schema, abort, EmptySchema
from apiflask.fields import Integer, String, Boolean, List
from apiflask.validators import Range
from pathlib import Path


app = APIFlask(__name__)
db_uri = 'sqlite:///:memory:' # in-memory database
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SYNC_LOCAL_SPEC'] = True
app.config['LOCAL_SPEC_PATH'] = Path(str(app.root_path)) / 'openapi.json'
db = SQLAlchemy(app)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    author = db.Column(db.String)

    __table_args__ = (
        UniqueConstraint('title', 'author', name='unique_item'),
    )

    def __init__(self, title: str, author: str):
        super().__init__(title=title, author = author)

    def to_dict(self) -> dict[str, object]:
        return {'id': self.id, 'title': self.title, 'author': self.author}


class BookIn(Schema):
    title = String(required=True)
    author = String(required=True)


class BookOut(Schema):
    id = Integer(dump_only=True)
    title = String(required=True)
    author = String(required=True)


class BookAll(Schema):
    results = List(BookOut)


class BookId(Schema):
    id = Integer(required=True)


class BookDeletion(Schema):
    success = Boolean(required=True)


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def index():
    """Landing page."""
    return "Hello World!"


@app.route('/books/<id>', methods=['GET'])
@app.input(BookId)
@app.output(BookOut)
def get_book(id: int):
    """Get a specified book from the database based on its id."""
    result = db.session.query(Book).filter(Book.id == id).one_or_none()

    if result is None:
        return make_response(jsonify({'error': 'Book not found!'}), 404)
    else:
        return make_response(jsonify(result.to_dict()), 200)


@app.route('/books/title/<title>', methods=['GET'])
def get_books_by_title(title: str):
    """Get a list of books with the specified title."""
    return make_response(jsonify({
        "results": db.session.query(Book).filter(Book.title == title).all()
    }), 200)


@app.route('/books', methods=['GET'])
@app.input(EmptySchema)
@app.output(schema=BookOut)
def get_all_books():
    """Get all the books stored in the database. If no books are stored, return an empty list."""
    return make_response(jsonify(db.session.query(Book).all()), 200)


@app.route('/books', methods=['POST'])
@app.output(schema=BookOut)
def create_book():
    """Add a new book to the database."""
    data = request.get_json()
    book = Book(title=data['title'], author=data['author'])
    db.session.add(book)
    db.session.commit()
    return make_response(jsonify(book.to_dict()), 201)


@app.route('/books', methods=['PUT'])
@app.output(schema=BookOut)
def mutate_book():
    """Modify an existing book in the database."""
    data = request.get_json()
    book = db.session.query(Book).filter(Book.id == data['id']).one_or_none()
    book.title = data['title']
    book.author = data['author']
    db.session.add(book)
    db.session.commit()
    return make_response(jsonify(book.to_dict()), 200)


@app.route('/books/<id>', methods=['DELETE'])
@app.output(schema=BookDeletion)
def delete_book(id: int):
    """Delete an existing book from the database by its id."""
    db.session.delete(db.session.query(Book).filter(Book.id == id).one_or_none())
    return make_response(jsonify({'success': True}), 200)


if __name__ == '__main__':
    app.run(debug=True)
