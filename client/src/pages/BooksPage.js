import { useState, useEffect } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import './BooksPage.css';

function Books() {
  const [books, setBooks] = useState([]);
  const [reviews, setReviews] = useState({});
  const [showForm, setShowForm] = useState(false);
  const [editingBook, setEditingBook] = useState(null);
  const [showReviewForm, setShowReviewForm] = useState({});
  const [editingReview, setEditingReview] = useState(null);
  const currentUser = JSON.parse(localStorage.getItem('user') || 'null');

  useEffect(() => {
    fetchBooks();
    fetchReviews();
  }, []);

  const fetchBooks = async () =>  {
    const token = localStorage.getItem('token');
    if (!token) return;
    const response = await fetch('http://localhost:5000/books', {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      setBooks(data);
    } else {
      setBooks([]);
    }
  };

  const fetchReviews = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    const response = await fetch('http://localhost:5000/reviews', {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      const reviewsByBook = {};
      data.forEach(review => {
        if (!reviewsByBook[review.book_id]) reviewsByBook[review.book_id] = [];
        reviewsByBook[review.book_id].push(review);
      });
      setReviews(reviewsByBook);
    } else {
      setReviews({});
    }
  };

  const handleEdit = (book) => {
    setEditingBook(book);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`http://localhost:5000/books/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (response.ok) {
      fetchBooks();
    } else {
      alert('Failed to delete book');
    }
  };

  const handleAddReview = (bookId) => {
    setShowReviewForm({ ...showReviewForm, [bookId]: true });
    setEditingReview(null);
  };

  const handleEditReview = (review) => {
    setEditingReview(review);
    setShowReviewForm({ ...showReviewForm, [review.book_id]: true });
  };

  const handleDeleteReview = async (id) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`http://localhost:5000/reviews/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (response.ok) {
      fetchReviews();
    } else {
      alert('Failed to delete review');
    }
  };

  return (
    <div className="books">
      <h2>Books</h2>
      <button onClick={() => { setShowForm(!showForm); setEditingBook(null); }}>
        {showForm ? 'Cancel' : 'Add Book'}
      </button>
      {showForm && <BookForm onAdd={fetchBooks} editingBook={editingBook} onCancel={() => setShowForm(false)} />}
      <div className="books-list">
        {books.map(book => (
          <div key={book.id} className="book-card">
            <h3>{book.title}</h3>
            <p>Author: {book.author}</p>
            <p>Year: {book.year_published}</p>
            <p>{book.description}</p>
            {currentUser && book.user && currentUser.id === book.user.id && (
              <>
                <button onClick={() => handleEdit(book)}>Edit</button>
                <button onClick={() => handleDelete(book.id)}>Delete</button>
              </>
            )}
            <div className="reviews">
              <h4>Reviews</h4>
              {reviews[book.id]?.map(review => (
                <div key={review.id} className="review">
                  <p>Rating: {review.rating}/5</p>
                  <p>{review.comment}</p>
                  <p>By: {review.user.username}</p>
                  {currentUser && review.user && currentUser.id === review.user.id && (
                    <>
                      <button onClick={() => handleEditReview(review)}>Edit</button>
                      <button onClick={() => handleDeleteReview(review.id)}>Delete</button>
                    </>
                  )}
                </div>
              ))}
              <button onClick={() => handleAddReview(book.id)}>
                {showReviewForm[book.id] ? 'Cancel' : 'Add Review'}
              </button>
              {showReviewForm[book.id] && (
                <ReviewForm
                  bookId={book.id}
                  onAdd={fetchReviews}
                  editingReview={editingReview}
                  onCancel={() => setShowReviewForm({ ...showReviewForm, [book.id]: false })}
                />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function BookForm({ onAdd, editingBook, onCancel }) {
  const validationSchema = Yup.object({
    title: Yup.string().required('Title is required'),
    author: Yup.string().required('Author is required'),
    year_published: Yup.number().integer('Year must be a whole number').min(1000, 'Year must be at least 1000').max(new Date().getFullYear(), 'Year cannot be in the future').required('Year is required'),
    description: Yup.string().required('Description is required')
  });

  const handleSubmit = async (values) => {
    const token = localStorage.getItem('token');
    const method = editingBook ? 'PATCH' : 'POST';
    const url = editingBook ? `http://localhost:5000/books/${editingBook.id}` : 'http://localhost:5000/books';
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(values)
    });
    if (response.ok) {
      onAdd();
      if (onCancel) onCancel();
    } else {
      alert('Failed to save book');
    }
  };

  return (
    <Formik
      initialValues={editingBook || { title: '', author: '', year_published: '', description: '' }}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
      enableReinitialize={true}
    >
      <Form className="book-form">
        <div>
          <Field name="title" type="text" placeholder="Title" />
          <ErrorMessage name="title" component="div" className="error" />
        </div>
        <div>
          <Field name="author" type="text" placeholder="Author" />
          <ErrorMessage name="author" component="div" className="error" />
        </div>
        <div>
          <Field name="year_published" type="number" placeholder="Year Published" />
          <ErrorMessage name="year_published" component="div" className="error" />
        </div>
        <div>
          <Field as="textarea" name="description" placeholder="Description" />
          <ErrorMessage name="description" component="div" className="error" />
        </div>
        <button type="submit">{editingBook ? 'Update Book' : 'Add Book'}</button>
        {onCancel && <button type="button" onClick={onCancel}>Cancel</button>}
      </Form>
    </Formik>
  );
}

function ReviewForm({ bookId, onAdd, editingReview, onCancel }) {
  const validationSchema = Yup.object({
    rating: Yup.number().integer('Rating must be a whole number').min(1, 'Rating must be at least 1').max(5, 'Rating cannot be more than 5').required('Rating is required'),
    comment: Yup.string().required('Comment is required')
  });

  const handleSubmit = async (values) => {
    const token = localStorage.getItem('token');
    const method = editingReview ? 'PATCH' : 'POST';
    const url = editingReview ? `http://localhost:5000/reviews/${editingReview.id}` : 'http://localhost:5000/reviews';
    const body = editingReview ? { ...values } : { ...values, book_id: bookId };
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(body)
    });
    if (response.ok) {
      onAdd();
      if (onCancel) onCancel();
    } else {
      alert('Failed to save review');
    }
  };

  return (
    <Formik
      initialValues={editingReview || { rating: '', comment: '' }}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
      enableReinitialize={true}
    >
      <Form className="review-form">
        <div>
          <Field name="rating" type="number" placeholder="Rating (1-5)" />
          <ErrorMessage name="rating" component="div" className="error" />
        </div>
        <div>
          <Field as="textarea" name="comment" placeholder="Comment" />
          <ErrorMessage name="comment" component="div" className="error" />
        </div>
        <button type="submit">{editingReview ? 'Update Review' : 'Add Review'}</button>
        {onCancel && <button type="button" onClick={onCancel}>Cancel</button>}
      </Form>
    </Formik>
  );
}

export default Books;