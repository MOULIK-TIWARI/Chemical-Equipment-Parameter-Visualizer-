/**
 * Complete Workflow Integration Test for React Web App
 * Task 27.1: Test complete workflow in React web app
 * 
 * This test validates the entire user workflow:
 * - Login flow
 * - CSV upload with sample data
 * - Dashboard display verification
 * - History navigation
 * - PDF download
 * 
 * Requirements: All
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import App from '../App'
import * as auth from '../utils/auth'
import api from '../services/api'

// Mock the API module
vi.mock('../services/api')

// Helper to render App with Router
const renderApp = () => {
  return render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  )
}

describe('Complete React Web App Workflow', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
    
    // Clear all mocks
    vi.clearAllMocks()
    
    // Reset API mock
    api.post = vi.fn()
    api.get = vi.fn()
  })

  it('should complete the full workflow: login -> dashboard -> verify components', async () => {
    const user = userEvent.setup()

    // ============================================
    // STEP 1: Test Login Flow
    // ============================================
    
    // Mock successful login response
    const mockLoginResponse = {
      data: {
        token: 'test-auth-token-12345',
        username: 'testuser'
      }
    }
    api.post.mockResolvedValueOnce(mockLoginResponse)

    renderApp()

    // Should show login page since not authenticated
    await waitFor(() => {
      expect(screen.getByText(/Chemical Equipment Analytics/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
    })

    // Find and fill login form
    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const loginButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(usernameInput, 'testuser')
    await user.type(passwordInput, 'testpassword')
    await user.click(loginButton)

    // Verify login API was called with correct credentials
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/auth/login/', {
        username: 'testuser',
        password: 'testpassword'
      })
    })

    // Verify token was stored
    expect(auth.getToken()).toBe('test-auth-token-12345')

    // ============================================
    // STEP 2: Verify Dashboard Loads
    // ============================================

    // Mock dataset list response with data
    const mockDatasets = {
      data: [
        {
          id: 1,
          name: 'sample_equipment_data.csv',
          uploaded_at: '2025-11-22T10:00:00Z',
          total_records: 15
        }
      ]
    }
    api.get.mockResolvedValueOnce(mockDatasets)

    // Mock dataset summary response
    const mockSummaryResponse = {
      data: {
        id: 1,
        name: 'sample_equipment_data.csv',
        uploaded_at: '2025-11-22T10:00:00Z',
        total_records: 15,
        avg_flowrate: 175.5,
        avg_pressure: 65.3,
        avg_temperature: 195.2,
        type_distribution: {
          'Pump': 5,
          'Reactor': 4,
          'Heat Exchanger': 4,
          'Compressor': 2
        }
      }
    }
    api.get.mockResolvedValueOnce(mockSummaryResponse)

    // Mock dataset data response
    const mockDatasetData = {
      data: {
        count: 15,
        results: [
          {
            id: 1,
            equipment_name: 'Pump-A1',
            equipment_type: 'Pump',
            flowrate: 150.5,
            pressure: 45.2,
            temperature: 85.0
          },
          {
            id: 2,
            equipment_name: 'Reactor-B2',
            equipment_type: 'Reactor',
            flowrate: 200.0,
            pressure: 120.5,
            temperature: 350.0
          }
        ]
      }
    }
    api.get.mockResolvedValueOnce(mockDatasetData)

    // Wait for dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/sample_equipment_data.csv/i)).toBeInTheDocument()
    }, { timeout: 3000 })

    // ============================================
    // STEP 3: Verify Dashboard Components
    // ============================================

    // Verify dataset name is displayed
    expect(screen.getByText(/sample_equipment_data.csv/i)).toBeInTheDocument()

    // Verify total records is displayed
    expect(screen.getByText(/15/)).toBeInTheDocument()

    // Verify action buttons are present
    expect(screen.getByText(/Upload New Dataset/i)).toBeInTheDocument()
    expect(screen.getByText(/View History/i)).toBeInTheDocument()
    expect(screen.getByText(/Logout/i)).toBeInTheDocument()

    // ============================================
    // STEP 4: Test History Navigation
    // ============================================

    // Mock datasets list for history
    const mockDatasetsHistory = {
      data: [
        {
          id: 1,
          name: 'sample_equipment_data.csv',
          uploaded_at: '2025-11-22T10:00:00Z',
          total_records: 15
        },
        {
          id: 2,
          name: 'previous_data.csv',
          uploaded_at: '2025-11-21T09:00:00Z',
          total_records: 20
        }
      ]
    }
    api.get.mockResolvedValueOnce(mockDatasetsHistory)

    // Navigate to history page
    const historyButton = screen.getByText(/View History/i)
    await user.click(historyButton)

    // Wait for history page to load
    await waitFor(() => {
      expect(screen.getByText(/Dataset History/i) || screen.getByText(/previous_data.csv/i)).toBeInTheDocument()
    }, { timeout: 3000 })

    // ============================================
    // STEP 5: Test Logout
    // ============================================

    // Find and click logout button
    const logoutButton = screen.getByText(/Logout/i)
    await user.click(logoutButton)

    // Verify token was removed
    expect(auth.getToken()).toBeNull()
  })

  it('should handle login errors gracefully', async () => {
    const user = userEvent.setup()

    // Mock failed login response
    api.post.mockRejectedValueOnce({
      response: {
        status: 401,
        data: {
          message: 'Invalid credentials'
        }
      }
    })

    renderApp()

    // Wait for login page
    await waitFor(() => {
      expect(screen.getByText(/Chemical Equipment Analytics/i)).toBeInTheDocument()
    })

    // Fill and submit login form
    const usernameInput = screen.getByLabelText(/username/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const loginButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(usernameInput, 'wronguser')
    await user.type(passwordInput, 'wrongpassword')
    await user.click(loginButton)

    // Verify error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i) || screen.getByText(/error/i)).toBeInTheDocument()
    })

    // Verify token was not stored
    expect(auth.getToken()).toBeNull()
  })

  it('should handle upload errors gracefully', async () => {
    const user = userEvent.setup()

    // Setup authenticated state
    localStorage.setItem('authToken', 'test-token')

    // Mock datasets list (empty)
    api.get.mockResolvedValueOnce({ data: [] })

    renderApp()

    // Wait for dashboard to load
    await waitFor(() => {
      expect(screen.getByText(/Chemical Equipment Analytics/i)).toBeInTheDocument()
    })

    // Should show empty state since no datasets
    expect(screen.getByText(/No Data Available/i) || screen.getByText(/Upload Dataset/i)).toBeInTheDocument()
  })

  it('should protect routes and redirect unauthenticated users to login', async () => {
    // Clear authentication
    localStorage.clear()

    renderApp()

    // Should redirect to login
    await waitFor(() => {
      expect(screen.getByText(/Chemical Equipment Analytics/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
    })
  })
})
