import axios from 'axios'
import { getToken, logout } from '../utils/auth'

// Create axios instance with base URL configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
})

// Request interceptor to add authentication token
api.interceptors.request.use(
  (config) => {
    // Get token using auth utilities
    const token = getToken()
    
    // If token exists, add it to request headers
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    
    return config
  },
  (error) => {
    // Handle request error
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    // Return successful response as-is
    return response
  },
  (error) => {
    // Handle different error scenarios
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Unauthorized - clear authentication data using auth utilities
          logout()
          
          // Only redirect if not already on login page
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          
          error.message = data.message || 'Authentication failed. Please login again.'
          break
          
        case 403:
          // Forbidden
          error.message = data.message || 'You do not have permission to perform this action.'
          break
          
        case 404:
          // Not found
          error.message = data.message || 'The requested resource was not found.'
          break
          
        case 400:
          // Bad request - validation errors
          error.message = data.message || data.error || 'Invalid request. Please check your input.'
          break
          
        case 500:
          // Server error
          error.message = data.message || 'An internal server error occurred. Please try again later.'
          break
          
        default:
          error.message = data.message || 'An unexpected error occurred.'
      }
    } else if (error.request) {
      // Request was made but no response received
      error.message = 'Unable to connect to the server. Please check your internet connection.'
    } else {
      // Something else happened
      error.message = error.message || 'An unexpected error occurred.'
    }
    
    return Promise.reject(error)
  }
)

export default api
