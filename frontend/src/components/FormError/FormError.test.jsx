import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import FormError from './FormError'

describe('FormError', () => {
  it('renders single error string', () => {
    render(<FormError error="This is an error" />)
    
    expect(screen.getByText('This is an error')).toBeInTheDocument()
  })

  it('renders multiple errors from object', () => {
    const errors = {
      username: 'Username is required',
      password: 'Password must be at least 8 characters'
    }
    
    render(<FormError errors={errors} />)
    
    expect(screen.getByText(/username:/i)).toBeInTheDocument()
    expect(screen.getByText(/Username is required/)).toBeInTheDocument()
    expect(screen.getByText(/password:/i)).toBeInTheDocument()
    expect(screen.getByText(/Password must be at least 8 characters/)).toBeInTheDocument()
  })

  it('renders array of errors for a field', () => {
    const errors = {
      email: ['Email is required', 'Email format is invalid']
    }
    
    render(<FormError errors={errors} />)
    
    expect(screen.getByText(/Email is required/)).toBeInTheDocument()
    expect(screen.getByText(/Email format is invalid/)).toBeInTheDocument()
  })

  it('returns null when no errors provided', () => {
    const { container } = render(<FormError />)
    
    expect(container.firstChild).toBeNull()
  })

  it('returns null when errors object is empty', () => {
    const { container } = render(<FormError errors={{}} />)
    
    expect(container.firstChild).toBeNull()
  })

  it('displays error icon', () => {
    render(<FormError error="Test error" />)
    
    expect(screen.getByText('⚠')).toBeInTheDocument()
  })
})
