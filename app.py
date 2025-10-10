from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db_uri = 'sqlite:///:memory:' # in-memory database
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    author = db.Column(db.String)

    def __init__(self, title: str, author: str):
        super().__init__(title=title, author = author)

    def to_dict(self) -> dict[str, object]:
        return {'id': self.id, 'title': self.title, 'author': self.author}


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def index():
    return "Hello World!"


@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    book = Book(title=data['title'], author=data['author'])
    db.session.add(book)
    db.session.commit()
    return make_response(jsonify(book.to_dict()), 201)


if __name__ == '__main__':
    app.run(debug=True)
