# Authentication Utilities Usage Guide

This document describes the authentication utilities implemented for the Chemical Equipment Analytics application.

## Overview

The authentication utilities provide a centralized way to manage authentication tokens and user session data in localStorage. These utilities are used throughout the application to handle login, logout, and authentication state validation.

## Available Functions

### Token Management

#### `getToken()`
Retrieves the authentication token from localStorage.
```javascript
import { getToken } from '../utils/auth'

const token = getToken()
// Returns: string | null
```

#### `setToken(token)`
Stores the authentication token in localStorage.
```javascript
import { setToken } from '../utils/auth'

setToken('your-auth-token-here')
```

#### `removeToken()`
Removes the authentication token from localStorage.
```javascript
import { removeToken } from '../utils/auth'

removeToken()
```

### Username Management

#### `getUsername()`
Retrieves the stored username from localStorage.
```javascript
import { getUsername } from '../utils/auth'

const username = getUsername()
// Returns: string | null
```

#### `setUsername(username)`
Stores the username in localStorage.
```javascript
import { setUsername } from '../utils/auth'

setUsername('john_doe')
```

#### `removeUsername()`
Removes the username from localStorage.
```javascript
import { removeUsername } from '../utils/auth'

removeUsername()
```

### Authentication State

#### `isAuthenticated()`
Checks if the user is currently authenticated by validating token existence.
```javascript
import { isAuthenticated } from '../utils/auth'

if (isAuthenticated()) {
  // User is logged in
} else {
  // User is not logged in
}
```

#### `validateToken(token)`
Validates the format of an authentication token.
```javascript
import { validateToken } from '../utils/auth'

const isValid = validateToken('some-token')
// Returns: boolean
```

### Session Management

#### `logout()`
Logs out the user by clearing all authentication data (token and username).
```javascript
import { logout } from '../utils/auth'

logout()
// Clears both token and username from localStorage
```

#### `clearAuth()`
Alias for `logout()`. Clears all authentication data.
```javascript
import { clearAuth } from '../utils/auth'

clearAuth()
```

## Usage Examples

### Login Flow
```javascript
import { setToken, setUsername } from '../utils/auth'

// After successful login API call
const response = await api.post('/auth/login/', { username, password })
const { token } = response.data

// Store authentication data
setToken(token)
setUsername(username)

// Redirect to dashboard
navigate('/dashboard')
```

### Logout Flow
```javascript
import { logout } from '../utils/auth'
import { useNavigate } from 'react-router-dom'

const handleLogout = () => {
  // Clear all authentication data
  logout()
  
  // Redirect to login page
  navigate('/login')
}
```

### Protected Route
```javascript
import { isAuthenticated } from '../utils/auth'
import { Navigate } from 'react-router-dom'

function PrivateRoute({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  return children
}
```

### API Request with Token
```javascript
import { getToken } from '../utils/auth'

// The API service automatically adds the token to requests
// via the request interceptor, but you can also access it manually:
const token = getToken()
if (token) {
  // Make authenticated request
}
```

### Automatic Logout on 401
The API service automatically handles 401 Unauthorized responses by:
1. Calling `logout()` to clear authentication data
2. Redirecting to the login page

This is configured in the API response interceptor.

## Requirements Satisfied

This implementation satisfies **Requirement 6.5**:
- WHEN a User successfully authenticates, THE System SHALL maintain the session for subsequent API requests

The utilities provide:
- ✅ Token storage and retrieval
- ✅ Logout functionality
- ✅ Token validation
- ✅ Session management
- ✅ Integration with API service for automatic token injection
- ✅ Automatic cleanup on authentication failure
