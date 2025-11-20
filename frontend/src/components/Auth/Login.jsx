import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../services/api'
import { setToken, setUsername as saveUsername } from '../../utils/auth'
import './Login.css'

function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Clear previous errors
    setError('')
    
    // Basic validation
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password')
      return
    }
    
    setLoading(true)
    
    try {
      // Call login API endpoint
      const response = await api.post('/auth/login/', {
        username: username.trim(),
        password: password
      })
      
      // Extract token from response
      const { token } = response.data
      
      if (token) {
        // Store authentication token using auth utilities
        setToken(token)
        
        // Store username for display purposes using auth utilities
        saveUsername(username.trim())
        
        // Redirect to dashboard on success
        navigate('/dashboard')
      } else {
        setError('Login failed: No token received')
      }
    } catch (err) {
      // Handle API errors
      setError(err.message || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Chemical Equipment Analytics</h2>
        <p className="login-subtitle">Sign in to your account</p>
        
        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
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
