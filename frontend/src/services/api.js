/**
 * API Service for Chemical Equipment Analytics Web Application
 * 
 * This module provides a configured axios instance for communicating with
 * the Django REST API backend. It handles:
 * - Base URL configuration
 * - Authentication token injection
 * - Global error handling
 * - Automatic logout on authentication failures
 * 
 * Requirements: 1.1, 2.4, 4.3, 5.1, 6.1, 6.5
 */

import axios from 'axios'
import { getToken, logout } from '../utils/auth'

/**
 * Create axios instance with base URL configuration
 * 
 * The base URL is read from environment variables (VITE_API_BASE_URL)
 * or defaults to localhost:8000 for development.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout for all requests
})

/**
 * Request interceptor to add authentication token
 * 
 * This interceptor runs before every request and automatically adds
 * the authentication token to the Authorization header if available.
 * 
 * Requirements: 6.1, 6.5
 */
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage using auth utilities
    const token = getToken()
    
    // If token exists, add it to request headers
    // Backend expects format: "Token <token_value>"
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    
    return config
  },
  (error) => {
    // Handle request configuration errors
    return Promise.reject(error)
  }
)

/**
 * Response interceptor for global error handling
 * 
 * This interceptor processes all API responses and provides consistent
 * error handling across the application. It:
 * - Passes through successful responses unchanged
 * - Transforms error responses into user-friendly messages
 * - Automatically handles authentication failures
 * - Redirects to login on 401 errors
 * 
 * Requirements: 1.4, 6.4
 */
api.interceptors.response.use(
  (response) => {
    // Return successful response as-is
    return response
  },
  (error) => {
    // Handle different error scenarios
    if (error.response) {
      // Server responded with an error status code
      const { status, data } = error.response
      
      // Process error based on HTTP status code
      switch (status) {
        case 401:
          // Unauthorized - authentication failed or token expired
          // Clear authentication data using auth utilities
          logout()
          
          // Redirect to login page (avoid redirect loop if already on login)
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          
          // Set user-friendly error message
          error.message = data.message || 'Authentication failed. Please login again.'
          break
          
        case 403:
          // Forbidden - user doesn't have permission
          error.message = data.message || 'You do not have permission to perform this action.'
          break
          
        case 404:
          // Not found - resource doesn't exist
          error.message = data.message || 'The requested resource was not found.'
          break
          
        case 400:
          // Bad request - validation errors or invalid input
          error.message = data.message || data.error || 'Invalid request. Please check your input.'
          break
          
        case 500:
          // Internal server error
          error.message = data.message || 'An internal server error occurred. Please try again later.'
          break
          
        default:
          // Other error status codes
          error.message = data.message || 'An unexpected error occurred.'
      }
    } else if (error.request) {
      // Request was made but no response received (network error)
      error.message = 'Unable to connect to the server. Please check your internet connection.'
    } else {
      // Something else happened during request setup
      error.message = error.message || 'An unexpected error occurred.'
    }
    
    // Reject the promise with the enhanced error
    return Promise.reject(error)
  }
)

export default api
