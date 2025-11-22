/**
 * Login Component for Chemical Equipment Analytics
 * 
 * Provides user authentication interface with:
 * - Username and password input fields
 * - Form validation
 * - API integration for authentication
 * - Error handling and user feedback
 * - Automatic redirect to dashboard on success
 * 
 * Requirements: 6.2, 6.4
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../services/api'
import { setToken, setUsername as saveUsername } from '../../utils/auth'
import { useToast } from '../Toast/ToastContainer'
import FormError from '../FormError/FormError'
import './Login.css'

/**
 * Login component
 * 
 * Handles user authentication by:
 * 1. Collecting username and password
 * 2. Validating input fields
 * 3. Calling the authentication API
 * 4. Storing the authentication token
 * 5. Redirecting to the dashboard
 * 
 * @returns {JSX.Element} Login form component
 */
function Login() {
  // Component state
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  // Hooks for navigation and notifications
  const navigate = useNavigate()
  const toast = useToast()

  /**
   * Handle form submission
   * 
   * Validates input, calls the login API, stores the token,
   * and redirects to the dashboard on success.
   * 
   * @param {Event} e - Form submit event
   */
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Clear previous errors
    setError('')
    
    // Basic client-side validation
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password')
      return
    }
    
    // Set loading state to disable form during API call
    setLoading(true)
    
    try {
      // Call login API endpoint (POST /api/auth/login/)
      const response = await api.post('/auth/login/', {
        username: username.trim(),
        password: password
      })
      
      // Extract token from response
      const { token } = response.data
      
      if (token) {
        // Store authentication token in localStorage using auth utilities
        setToken(token)
        
        // Store username for display purposes
        saveUsername(username.trim())
        
        // Show success notification
        toast.showSuccess('Login successful! Redirecting...')
        
        // Redirect to dashboard on successful authentication
        navigate('/dashboard')
      } else {
        // Handle unexpected response format (no token)
        const errorMsg = 'Login failed: No token received'
        setError(errorMsg)
        toast.showError(errorMsg)
      }
    } catch (err) {
      // Handle API errors (network errors, invalid credentials, etc.)
      // Error message is set by the API interceptor
      const errorMsg = err.message || 'Login failed. Please check your credentials.'
      setError(errorMsg)
      toast.showError(errorMsg)
    } finally {
      // Reset loading state
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Chemical Equipment Analytics</h2>
        <p className="login-subtitle">Sign in to your account</p>
        
        <form onSubmit={handleSubmit} className="login-form">
          {error && <FormError error={error} />}
          
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              disabled={loading}
              autoComplete="username"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              disabled={loading}
              autoComplete="current-password"
            />
          </div>
          
          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login
