from app import app, db
from models import User, Book, Review

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Seed users
        user1 = User(username='john_doe', email='john@example.com')
        user1.set_password('password123')
        user2 = User(username='jane_smith', email='jane@example.com')
        user2.set_password('password123')
        db.session.add_all([user1, user2])
        db.session.commit()  # Commit to get ids

        # Seed books
        book1 = Book(title='1984', author='George Orwell', year_published=1949, description='A dystopian novel about totalitarianism.', user_id=user1.id)
        book2 = Book(title='To Kill a Mockingbird', author='Harper Lee', year_published=1960, description='A classic American novel about racism and injustice.', user_id=user2.id)
        book3 = Book(title='Pride and Prejudice', author='Jane Austen', year_published=1813, description='A romantic novel about manners and marriage.', user_id=user1.id)
        book4 = Book(title='The Great Gatsby', author='F. Scott Fitzgerald', year_published=1925, description='A story of the Jazz Age and the American Dream.', user_id=user1.id)
        book5 = Book(title='The Catcher in the Rye', author='J.D. Salinger', year_published=1951, description='A controversial novel about teenage angst.', user_id=user2.id)
        book6 = Book(title='Harry Potter and the Sorcerer\'s Stone', author='J.K. Rowling', year_published=1997, description='The first book in the Harry Potter series.', user_id=user1.id)
        book7 = Book(title='The Lord of the Rings', author='J.R.R. Tolkien', year_published=1954, description='An epic fantasy adventure.', user_id=user2.id)
        book8 = Book(title='The Hobbit', author='J.R.R. Tolkien', year_published=1937, description='A fantasy adventure novel.', user_id=user1.id)
        book9 = Book(title='Dune', author='Frank Herbert', year_published=1965, description='A science fiction epic set on the desert planet Arrakis.', user_id=user2.id)
        book10 = Book(title='Neuromancer', author='William Gibson', year_published=1984, description='A cyberpunk novel that defined the genre.', user_id=user1.id)
        book11 = Book(title='The Hitchhiker\'s Guide to the Galaxy', author='Douglas Adams', year_published=1979, description='A comedic science fiction series.', user_id=user2.id)
        book12 = Book(title='Ender\'s Game', author='Orson Scott Card', year_published=1985, description='A military science fiction novel.', user_id=user1.id)
        book13 = Book(title='The Name of the Wind', author='Patrick Rothfuss', year_published=2007, description='An epic fantasy novel.', user_id=user2.id)
        book14 = Book(title='American Gods', author='Neil Gaiman', year_published=2001, description='A blend of fantasy, mythology, and Americana.', user_id=user1.id)
        book15 = Book(title='The Martian', author='Andy Weir', year_published=2011, description='A survival story on Mars.', user_id=user2.id)
        db.session.add_all([book1, book2, book3, book4, book5, book6, book7, book8, book9, book10, book11, book12, book13, book14, book15])
        db.session.commit()

        # Seed reviews
        review1 = Review(rating=5, comment='A masterpiece!', user_id=user2.id, book_id=book1.id)
        review2 = Review(rating=4, comment='Timeless story.', user_id=user1.id, book_id=book2.id)
        review3 = Review(rating=5, comment='Love the characters.', user_id=user2.id, book_id=book3.id)
        db.session.add_all([review1, review2, review3])

        db.session.commit()
        print('Database seeded!')

if __name__ == '__main__':
    seed_data()