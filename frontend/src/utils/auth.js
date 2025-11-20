/**
 * Authentication utilities for token management and validation
 * Requirements: 6.5
 */

const TOKEN_KEY = 'authToken'
const USERNAME_KEY = 'username'

/**
 * Retrieve the authentication token from localStorage
 * @returns {string|null} The authentication token or null if not found
 */
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * Store the authentication token in localStorage
 * @param {string} token - The authentication token to store
 */
export const setToken = (token) => {
  if (token && typeof token === 'string') {
    localStorage.setItem(TOKEN_KEY, token)
  }
}

/**
 * Remove the authentication token from localStorage
 */
export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY)
}

/**
 * Get the stored username
 * @returns {string|null} The username or null if not found
 */
export const getUsername = () => {
  return localStorage.getItem(USERNAME_KEY)
}

/**
 * Store the username in localStorage
 * @param {string} username - The username to store
 */
export const setUsername = (username) => {
  if (username && typeof username === 'string') {
    localStorage.setItem(USERNAME_KEY, username)
  }
}

/**
 * Remove the username from localStorage
 */
export const removeUsername = () => {
  localStorage.removeItem(USERNAME_KEY)
}

/**
 * Check if the user is authenticated by validating token existence
 * @returns {boolean} True if a valid token exists, false otherwise
 */
export const isAuthenticated = () => {
  const token = getToken()
  return !!token && token.length > 0
}

/**
 * Validate the authentication token format
 * Basic validation to check if token is a non-empty string
 * @param {string} token - The token to validate
 * @returns {boolean} True if token is valid format, false otherwise
 */
export const validateToken = (token) => {
  if (!token || typeof token !== 'string') {
    return false
  }
  
  // Check if token is not empty and has reasonable length
  const trimmedToken = token.trim()
  return trimmedToken.length > 0
}

/**
 * Logout the user by clearing all authentication data
 * Removes token and username from localStorage
 */
export const logout = () => {
  removeToken()
  removeUsername()
}

/**
 * Clear all authentication data (alias for logout)
 */
export const clearAuth = () => {
  logout()
}
