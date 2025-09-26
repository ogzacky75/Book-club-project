// src/pages/Login.js
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import './AuthPage.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

function Login() {
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const validationSchema = Yup.object({
    username: Yup.string().required('Username is required'),
    password: Yup.string().required('Password is required')
  });

  const handleSubmit = async (values, { setSubmitting }) => {
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values)
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/books');
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Could not connect to the server.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth">
      <h2>Login</h2>
      {error && <p className="error">{error}</p>}
      <Formik
        initialValues={{ username: '', password: '' }}
        validationSchema={validationSchema}
        onSubmit={handleSubmit}
      >
        <Form>
          <div>
            <Field name="username" type="text" placeholder="Username" />
            <ErrorMessage name="username" component="div" className="error" />
          </div>
          <div>
            <Field name="password" type="password" placeholder="Password" />
            <ErrorMessage name="password" component="div" className="error" />
          </div>
          <button type="submit">Login</button>
        </Form>
      </Formik>
    </div>
  );
}

export default Login;
