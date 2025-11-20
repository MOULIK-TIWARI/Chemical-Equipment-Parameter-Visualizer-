import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import './FileUpload.css'
import api from '../../services/api'

function FileUpload({ onUploadSuccess }) {
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const fileInputRef = useRef(null)

  // Validate file type (CSV only)
  const validateFile = (file) => {
    if (!file) {
      return 'No file selected'
    }

    // Check file extension
    const fileName = file.name.toLowerCase()
    if (!fileName.endsWith('.csv')) {
      return 'Invalid file type. Please select a CSV file.'
    }

    // Check MIME type
    const validMimeTypes = ['text/csv', 'application/vnd.ms-excel', 'text/plain']
    if (file.type && !validMimeTypes.includes(file.type)) {
      return 'Invalid file type. Please select a CSV file.'
    }

    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      return 'File size exceeds 10MB limit.'
    }

    return null
  }

  // Handle file selection
  const handleFileSelect = (file) => {
    setError('')
    
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      setSelectedFile(null)
      return
    }

    setSelectedFile(file)
  }

  // Handle file input change
  const handleFileInputChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  // Handle drag events
  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  // Handle click on drop zone
  const handleDropZoneClick = () => {
    fileInputRef.current?.click()
  }

  // Handle upload
  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }

    setIsUploading(true)
    setUploadProgress(0)
    setError('')

    try {
      // Create FormData with selected file
      const formData = new FormData()
      formData.append('file', selectedFile)

      // Call POST /api/datasets/upload/ endpoint
      const response = await api.post('/datasets/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          // Calculate and update upload progress
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          setUploadProgress(percentCompleted)
        },
      })

      // Handle success response
      setIsUploading(false)
      setUploadProgress(100)
      
      // Show success notification
      const datasetName = response.data.name || selectedFile.name
      setSuccessMessage(`Successfully uploaded ${datasetName}! Redirecting to dashboard...`)
      
      // Call success callback if provided, passing the response data
      if (onUploadSuccess) {
        onUploadSuccess(response.data)
      }

      // Redirect to dashboard with new dataset after a brief delay
      setTimeout(() => {
        // Navigate to dashboard, passing the dataset ID in state
        navigate('/dashboard', { 
          state: { 
            datasetId: response.data.id,
            isNewUpload: true 
          } 
        })
      }, 1500)

    } catch (err) {
      // Handle error responses
      setIsUploading(false)
      setUploadProgress(0)

      // Display validation errors to user
      if (err.response && err.response.data) {
        const errorData = err.response.data
        
        // Handle different error formats
        if (errorData.error) {
          setError(errorData.error)
        } else if (errorData.message) {
          setError(errorData.message)
        } else if (errorData.details) {
          // Handle detailed validation errors
          const detailMessages = Object.entries(errorData.details)
            .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
            .join('; ')
          setError(detailMessages || 'Validation error occurred')
        } else if (typeof errorData === 'string') {
          setError(errorData)
        } else {
          setError('Failed to upload file. Please try again.')
        }
      } else {
        // Use the error message from the interceptor
        setError(err.message || 'Failed to upload file. Please check your connection and try again.')
      }
    }
  }

  // Handle clear selection
  const handleClear = () => {
    setSelectedFile(null)
    setError('')
    setSuccessMessage('')
    setUploadProgress(0)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="file-upload-container">
      <h2>Upload CSV File</h2>
      <p className="upload-subtitle">Upload equipment data for analysis</p>

      {/* Drag and drop zone */}
      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleDropZoneClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />

        {!selectedFile ? (
          <>
            <div className="upload-icon">📁</div>
            <p className="drop-zone-text">
              Drag and drop your CSV file here
            </p>
            <p className="drop-zone-subtext">or click to browse</p>
            <p className="drop-zone-hint">CSV files only, max 10MB</p>
          </>
        ) : (
          <>
            <div className="file-icon">📄</div>
            <p className="file-name">{selectedFile.name}</p>
            <p className="file-size">
              {(selectedFile.size / 1024).toFixed(2)} KB
            </p>
          </>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Success message */}
      {successMessage && (
        <div className="success-message">
          ✓ {successMessage}
        </div>
      )}

      {/* Upload progress */}
      {isUploading && (
        <div className="progress-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <p className="progress-text">{uploadProgress}%</p>
        </div>
      )}

      {/* Action buttons */}
      <div className="button-group">
        {selectedFile && !isUploading && (
          <button
            className="clear-button"
            onClick={handleClear}
          >
            Clear
          </button>
        )}
        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={!selectedFile || isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
    </div>
  )
}

export default FileUpload
