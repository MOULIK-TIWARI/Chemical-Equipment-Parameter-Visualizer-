import React from 'react'
import './FormError.css'

function FormError({ error, errors }) {
  // Handle single error string
  if (error && typeof error === 'string') {
    return (
      <div className="form-error">
        <span className="form-error-icon">⚠</span>
        <span className="form-error-message">{error}</span>
      </div>
    )
  }

  // Handle multiple errors object
  if (errors && typeof errors === 'object') {
    const errorEntries = Object.entries(errors)
    
    if (errorEntries.length === 0) {
      return null
    }

    return (
      <div className="form-errors">
        {errorEntries.map(([field, messages]) => {
          const messageArray = Array.isArray(messages) ? messages : [messages]
          return messageArray.map((msg, index) => (
            <div key={`${field}-${index}`} className="form-error">
              <span className="form-error-icon">⚠</span>
              <span className="form-error-message">
                <strong>{field}:</strong> {msg}
              </span>
            </div>
          ))
        })}
      </div>
    )
  }

  return null
}

export default FormError
