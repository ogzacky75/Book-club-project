# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, User, Book, Review
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)
jwt = JWTManager(app)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    return jsonify({
        'message': 'Signup successful',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': username,
            'email': email
        }
    }), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': username,
            'email': user.email
        }
    }), 200

@app.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    user_id = get_jwt_identity()
    books = Book.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'year_published': book.year_published,
        'description': book.description,
        'user': {'id': book.user.id, 'username': book.user.username}
    } for book in books])

@app.route('/books', methods=['POST'])
@jwt_required()
def add_book():
    user_id = get_jwt_identity()
    data = request.get_json()
    book = Book(
        title=data['title'],
        author=data['author'],
        year_published=data['year_published'],
        description=data['description'],
        user_id=user_id
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Book added'}), 201

@app.route('/books/<int:id>', methods=['PATCH'])
@jwt_required()
def update_book(id):
    user_id = get_jwt_identity()
    book = Book.query.filter_by(id=id, user_id=user_id).first()
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    data = request.get_json()
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.year_published = data.get('year_published', book.year_published)
    book.description = data.get('description', book.description)
    db.session.commit()
    return jsonify({'message': 'Book updated'})

@app.route('/books/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    user_id = get_jwt_identity()
    book = Book.query.filter_by(id=id, user_id=user_id).first()
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})

@app.route('/reviews', methods=['GET'])
@jwt_required()
def get_reviews():
    user_id = get_jwt_identity()
    reviews = Review.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': review.id,
        'rating': review.rating,
        'comment': review.comment,
        'book_id': review.book_id,
        'user': {'id': review.user.id, 'username': review.user.username}
    } for review in reviews])

@app.route('/reviews', methods=['POST'])
@jwt_required()
def add_review():
    user_id = get_jwt_identity()
    data = request.get_json()
    review = Review(
        rating=data['rating'],
        comment=data['comment'],
        book_id=data['book_id'],
        user_id=user_id
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': 'Review added'}), 201

@app.route('/reviews/<int:id>', methods=['PATCH'])
@jwt_required()
def update_review(id):
    user_id = get_jwt_identity()
    review = Review.query.filter_by(id=id, user_id=user_id).first()
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    data = request.get_json()
    review.rating = data.get('rating', review.rating)
    review.comment = data.get('comment', review.comment)
    db.session.commit()
    return jsonify({'message': 'Review updated'})

@app.route('/reviews/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_review(id):
    user_id = get_jwt_identity()
    review = Review.query.filter_by(id=id, user_id=user_id).first()
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)