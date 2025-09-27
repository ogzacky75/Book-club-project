from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

# Import db and models
from models import db, User, Book, Review

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    # Init extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Create tables
    with app.app_context():
        db.create_all()

    # ------------------ ROUTES ------------------

    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        hashed_pw = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()

        token = create_access_token(identity=user.id)
        return jsonify({
            "access_token": token,
            "user": {"id": user.id, "username": user.username, "email": user.email}
        }), 201

    @app.route('/login', methods=['POST'])
    def login():
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_access_token(identity=user.id)
        return jsonify({
            "access_token": token,
            "user": {"id": user.id, "username": user.username, "email": user.email}
        }), 200

    # ----------- BOOK ROUTES ------------

    @app.route('/books', methods=['GET'])
    @jwt_required()
    def get_books():
        books = Book.query.all()
        result = []
        for b in books:
            result.append({
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "year_published": b.year_published,
                "description": b.description,
                "user": {
                    "id": b.user.id,
                    "username": b.user.username,
                    "email": b.user.email
                } if b.user else None
            })
        return jsonify(result), 200

    @app.route('/books', methods=['POST'])
    @jwt_required()
    def add_book():
        data = request.json
        current_user_id = get_jwt_identity()
        book = Book(
            title=data['title'],
            author=data['author'],
            year_published=data['year_published'],
            description=data['description'],
            user_id=current_user_id
        )
        db.session.add(book)
        db.session.commit()
        return jsonify({"msg": "Book added"}), 201

    @app.route('/books/<int:book_id>', methods=['PATCH'])
    @jwt_required()
    def update_book(book_id):
        book = Book.query.get_or_404(book_id)
        current_user_id = get_jwt_identity()
        if book.user_id != current_user_id:
            return jsonify({"error": "Unauthorized"}), 403
        data = request.json
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.year_published = data.get('year_published', book.year_published)
        book.description = data.get('description', book.description)
        db.session.commit()
        return jsonify({"msg": "Book updated"}), 200

    @app.route('/books/<int:book_id>', methods=['DELETE'])
    @jwt_required()
    def delete_book(book_id):
        book = Book.query.get_or_404(book_id)
        current_user_id = get_jwt_identity()
        if book.user_id != current_user_id:
            return jsonify({"error": "Unauthorized"}), 403
        db.session.delete(book)
        db.session.commit()
        return jsonify({"msg": "Book deleted"}), 200

    # ----------- REVIEW ROUTES ------------

    @app.route('/reviews', methods=['GET'])
    @jwt_required()
    def get_reviews():
        reviews = Review.query.all()
        result = []
        for r in reviews:
            result.append({
                "id": r.id,
                "rating": r.rating,
                "comment": r.comment,
                "book_id": r.book_id,
                "user": {
                    "id": r.user.id,
                    "username": r.user.username,
                    "email": r.user.email
                } if r.user else None
            })
        return jsonify(result), 200

    @app.route('/reviews', methods=['POST'])
    @jwt_required()
    def add_review():
        data = request.json
        current_user_id = get_jwt_identity()
        review = Review(
            rating=data['rating'],
            comment=data['comment'],
            book_id=data['book_id'],
            user_id=current_user_id
        )
        db.session.add(review)
        db.session.commit()
        return jsonify({"msg": "Review added"}), 201

    @app.route('/reviews/<int:review_id>', methods=['PATCH'])
    @jwt_required()
    def update_review(review_id):
        review = Review.query.get_or_404(review_id)
        current_user_id = get_jwt_identity()
        if review.user_id != current_user_id:
            return jsonify({"error": "Unauthorized"}), 403
        data = request.json
        review.rating = data.get('rating', review.rating)
        review.comment = data.get('comment', review.comment)
        db.session.commit()
        return jsonify({"msg": "Review updated"}), 200

    @app.route('/reviews/<int:review_id>', methods=['DELETE'])
    @jwt_required()
    def delete_review(review_id):
        review = Review.query.get_or_404(review_id)
        current_user_id = get_jwt_identity()
        if review.user_id != current_user_id:
            return jsonify({"error": "Unauthorized"}), 403
        db.session.delete(review)
        db.session.commit()
        return jsonify({"msg": "Review deleted"}), 200

    return app

# --- Run server ---
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
