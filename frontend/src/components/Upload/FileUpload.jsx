/**
 * FileUpload Component for Chemical Equipment Analytics
 * 
 * Provides CSV file upload functionality with:
 * - Drag-and-drop interface
 * - File type validation (CSV only)
 * - File size validation (max 10MB)
 * - Upload progress tracking
 * - Error handling and user feedback
 * - Automatic redirect to dashboard on success
 * 
 * Requirements: 1.1, 1.2, 1.3, 1.4
 */

import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import './FileUpload.css'
import api from '../../services/api'
import { useToast } from '../Toast/ToastContainer'
import FormError from '../FormError/FormError'

/**
 * FileUpload component
 * 
 * Handles CSV file upload by:
 * 1. Providing drag-and-drop and file selection interface
 * 2. Validating file type and size
 * 3. Uploading file to the backend API
 * 4. Tracking upload progress
 * 5. Redirecting to dashboard on success
 * 
 * @param {Object} props - Component props
 * @param {Function} props.onUploadSuccess - Callback function called on successful upload
 * @returns {JSX.Element} File upload component
 */
function FileUpload({ onUploadSuccess }) {
  // Hooks for navigation and notifications
  const navigate = useNavigate()
  const toast = useToast()
  
  // Component state
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  
  // Reference to hidden file input element
  const fileInputRef = useRef(null)

  /**
   * Validate file type and size
   * 
   * Checks that the file:
   * - Exists
   * - Has .csv extension
   * - Has valid MIME type
   * - Is under 10MB size limit
   * 
   * @param {File} file - File to validate
   * @returns {string|null} Error message if invalid, null if valid
   * 
   * Requirements: 1.3
   */
  const validateFile = (file) => {
    if (!file) {
      return 'No file selected'
    }

    // Check file extension
    const fileName = file.name.toLowerCase()
    if (!fileName.endsWith('.csv')) {
      return 'Invalid file type. Please select a CSV file.'
    }

    // Check MIME type (browsers may report different MIME types for CSV)
    const validMimeTypes = ['text/csv', 'application/vnd.ms-excel', 'text/plain']
    if (file.type && !validMimeTypes.includes(file.type)) {
      return 'Invalid file type. Please select a CSV file.'
    }

    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024 // 10MB in bytes
    if (file.size > maxSize) {
      return 'File size exceeds 10MB limit.'
    }

    return null
  }

  /**
   * Handle file selection
   * 
   * Validates the selected file and updates component state.
   * 
   * @param {File} file - Selected file
   */
  const handleFileSelect = (file) => {
    setError('')
    
    // Validate the file
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      setSelectedFile(null)
      return
    }

    // Store the valid file
    setSelectedFile(file)
  }

  /**
   * Handle file input change event
   * 
   * Called when user selects a file via the file input dialog.
   * 
   * @param {Event} e - Change event
   */
  const handleFileInputChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  /**
   * Handle drag enter event
   * 
   * Updates UI to show drag state.
   * 
   * @param {DragEvent} e - Drag event
   */
  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  /**
   * Handle drag leave event
   * 
   * Updates UI to remove drag state.
   * 
   * @param {DragEvent} e - Drag event
   */
  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  /**
   * Handle drag over event
   * 
   * Required to allow drop event.
   * 
   * @param {DragEvent} e - Drag event
   */
  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  /**
   * Handle drop event
   * 
   * Called when user drops a file onto the drop zone.
   * 
   * @param {DragEvent} e - Drop event
   */
  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    // Get the dropped files
    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      // Only handle the first file
      handleFileSelect(files[0])
    }
  }

  /**
   * Handle click on drop zone
   * 
   * Opens the file selection dialog.
   */
  const handleDropZoneClick = () => {
    fileInputRef.current?.click()
  }

  /**
   * Handle file upload
   * 
   * Uploads the selected file to the backend API with progress tracking.
   * On success, redirects to the dashboard.
   * 
   * Requirements: 1.1, 1.2, 1.4
   */
  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }

    // Set uploading state
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
        // Track upload progress
        onUploadProgress: (progressEvent) => {
          // Calculate percentage completed
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
      const successMsg = `Successfully uploaded ${datasetName}!`
      setSuccessMessage(successMsg)
      toast.showSuccess(successMsg)
      
      // Call success callback if provided
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

      let errorMsg = ''
      
      // Display validation errors to user
      if (err.response && err.response.data) {
        const errorData = err.response.data
        
        // Handle different error response formats from the API
        if (errorData.error) {
          errorMsg = errorData.error
        } else if (errorData.message) {
          errorMsg = errorData.message
        } else if (errorData.details) {
          // Handle detailed validation errors (field-specific errors)
          const detailMessages = Object.entries(errorData.details)
            .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
            .join('; ')
          errorMsg = detailMessages || 'Validation error occurred'
        } else if (typeof errorData === 'string') {
          errorMsg = errorData
        } else {
          errorMsg = 'Failed to upload file. Please try again.'
        }
      } else {
        // Use the error message from the API interceptor
        errorMsg = err.message || 'Failed to upload file. Please check your connection and try again.'
      }
      
      // Display error to user
      setError(errorMsg)
      toast.showError(errorMsg)
    }
  }

  /**
   * Handle clear selection
   * 
   * Resets the component state to allow selecting a new file.
   */
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
      {error && <FormError error={error} />}

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
