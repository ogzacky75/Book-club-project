from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity  # type: ignore
)
from flask_marshmallow import Marshmallow  # type: ignore
from config import Config
from models import db, User, Book, Review

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
jwt = JWTManager(app)
ma = Marshmallow(app)
db.init_app(app)

# ─────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)

class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        load_instance = True
        exclude = ('reviews',)
    user = ma.Nested(UserSchema)

class ReviewSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Review
        load_instance = True
    user = ma.Nested(UserSchema)
    book = ma.Nested(BookSchema)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
book_schema = BookSchema()
books_schema = BookSchema(many=True)
review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)

# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to Book Club API'})

# ─────────────────────────────────────────────────────────────
# Auth Routes
# ─────────────────────────────────────────────────────────────

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'User already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token, 'user': user_schema.dump(user)}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token, 'user': user_schema.dump(user)}), 200

# ─────────────────────────────────────────────────────────────
# User Routes
# ─────────────────────────────────────────────────────────────

@app.route('/users/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.get_or_404(id)
    return user_schema.jsonify(user)

# ─────────────────────────────────────────────────────────────
# Book Routes
# ─────────────────────────────────────────────────────────────

@app.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    books = Book.query.all()
    return books_schema.jsonify(books)

@app.route('/books', methods=['POST'])
@jwt_required()
def create_book():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    book = Book(
        title=data.get('title'),
        author=data.get('author'),
        year_published=data.get('year_published'),
        description=data.get('description'),
        user_id=current_user_id
    )

    db.session.add(book)
    db.session.commit()
    return book_schema.jsonify(book), 201

@app.route('/books/<int:id>', methods=['GET'])
@jwt_required()
def get_book(id):
    book = Book.query.get_or_404(id)
    return book_schema.jsonify(book)

@app.route('/books/<int:id>', methods=['PATCH'])
@jwt_required()
def update_book(id):
    current_user_id = get_jwt_identity()
    book = Book.query.get_or_404(id)

    if book.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    for key, value in data.items():
        if hasattr(book, key):
            setattr(book, key, value)

    db.session.commit()
    return book_schema.jsonify(book)

@app.route('/books/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    current_user_id = get_jwt_identity()
    book = Book.query.get_or_404(id)

    if book.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'}), 204

# ─────────────────────────────────────────────────────────────
# Review Routes
# ─────────────────────────────────────────────────────────────

@app.route('/reviews', methods=['GET'])
@jwt_required()
def get_reviews():
    reviews = Review.query.all()
    return reviews_schema.jsonify(reviews)

@app.route('/reviews', methods=['POST'])
@jwt_required()
def create_review():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    review = Review(
        rating=data.get('rating'),
        comment=data.get('comment'),
        user_id=current_user_id,
        book_id=data.get('book_id')
    )

    db.session.add(review)
    db.session.commit()
    return review_schema.jsonify(review), 201

@app.route('/reviews/<int:id>', methods=['PATCH'])
@jwt_required()
def update_review(id):
    current_user_id = get_jwt_identity()
    review = Review.query.get_or_404(id)

    if review.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    for key, value in data.items():
        if hasattr(review, key):
            setattr(review, key, value)

    db.session.commit()
    return review_schema.jsonify(review)

@app.route('/reviews/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_review(id):
    current_user_id = get_jwt_identity()
    review = Review.query.get_or_404(id)

    if review.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted'}), 204

# ─────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
