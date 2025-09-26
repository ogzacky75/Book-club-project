import './HomePage.css';

function Home() {
  return (
    <div className="home">
      <h1>Welcome to the Book Club!</h1>
      <p>Join our community of book lovers. Discover new books, share reviews, and connect with fellow readers.</p>
      <div className="features">
        <div className="feature">
          <h3>Browse Books</h3>
          <p>Explore a wide collection of books added by our members.</p>
        </div>
        <div className="feature">
          <h3>Rate & Review</h3>
          <p>Share your thoughts and rate the books you've read.</p>
        </div>
        <div className="feature">
          <h3>Connect</h3>
          <p>Meet other book enthusiasts and discuss your favorite reads.</p>
        </div>
      </div>
    </div>
  );
}

export default Home;