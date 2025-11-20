import { Navigate } from 'react-router-dom'
import { isAuthenticated } from '../../utils/auth'

function PrivateRoute({ children }) {
  // Check if user is authenticated
  if (!isAuthenticated()) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" replace />
  }

  // Render the protected component if authenticated
  return children
}

export default PrivateRoute
