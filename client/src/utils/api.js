// src/utils/api.js
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "https://book-club-project.onrender.com";

export async function fetchBooks() {
  try {
    const res = await fetch(`${API_BASE_URL}/books`);
    if (!res.ok) throw new Error(`Failed to fetch books: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("fetchBooks error:", err);
    throw err;
  }
}

export async function fetchReviews() {
  try {
    const res = await fetch(`${API_BASE_URL}/reviews`);
    if (!res.ok) throw new Error(`Failed to fetch reviews: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("fetchReviews error:", err);
    throw err;
  }
}

export async function loginUser(values) {
  try {
    const res = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Login failed");
    return data;
  } catch (err) {
    console.error("loginUser error:", err);
    throw err;
  }
}
