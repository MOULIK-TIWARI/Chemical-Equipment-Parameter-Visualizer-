import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import userEvent from '@testing-library/user-event'
import Toast from './Toast'

describe('Toast', () => {
  it('renders toast with message', () => {
    const onClose = vi.fn()
    render(<Toast message="Test message" type="info" onClose={onClose} />)
    
    expect(screen.getByText('Test message')).toBeInTheDocument()
  })

  it('renders success toast with correct styling', () => {
    const onClose = vi.fn()
    const { container } = render(<Toast message="Success!" type="success" onClose={onClose} />)
    
    expect(container.querySelector('.toast-success')).toBeInTheDocument()
  })

  it('renders error toast with correct styling', () => {
    const onClose = vi.fn()
    const { container } = render(<Toast message="Error!" type="error" onClose={onClose} />)
    
    expect(container.querySelector('.toast-error')).toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    render(<Toast message="Test" type="info" onClose={onClose} />)
    
    const closeButton = screen.getByRole('button')
    await user.click(closeButton)
    
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('auto-closes after duration', async () => {
    const onClose = vi.fn()
    render(<Toast message="Test" type="info" duration={100} onClose={onClose} />)
    
    await waitFor(() => expect(onClose).toHaveBeenCalled(), { timeout: 200 })
  })

  it('does not auto-close when duration is 0', async () => {
    const onClose = vi.fn()
    render(<Toast message="Test" type="info" duration={0} onClose={onClose} />)
    
    await new Promise(resolve => setTimeout(resolve, 100))
    expect(onClose).not.toHaveBeenCalled()
  })
})
