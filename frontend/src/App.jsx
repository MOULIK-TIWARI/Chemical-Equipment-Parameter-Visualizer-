import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import Login from './components/Auth/Login'
import Dashboard from './components/Dashboard/Dashboard'
import DatasetHistory from './components/History/DatasetHistory'
import PrivateRoute from './components/Auth/PrivateRoute'
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary'
import { ToastProvider } from './components/Toast/ToastContainer'

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <div className="App">
          <Routes>
            {/* Public route - Login */}
            <Route path="/login" element={<Login />} />
            
            {/* Protected routes */}
            <Route 
              path="/dashboard" 
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/history" 
              element={
                <PrivateRoute>
                  <DatasetHistory />
                </PrivateRoute>
              } 
            />
            
            {/* Default redirect to dashboard */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* Catch all - redirect to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </ToastProvider>
    </ErrorBoundary>
  )
}

export default App
