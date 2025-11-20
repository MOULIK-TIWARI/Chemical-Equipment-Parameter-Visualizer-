import React, { useState, useRef } from 'react'
import './FileUpload.css'

function FileUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState('')
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

  // Handle upload (placeholder for task 12.2)
  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }

    setIsUploading(true)
    setUploadProgress(0)
    setError('')

    // Simulate upload progress for now
    // This will be replaced with actual API call in task 12.2
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsUploading(false)
          
          // Call success callback if provided
          if (onUploadSuccess) {
            onUploadSuccess()
          }
          
          return 100
        }
        return prev + 10
      })
    }, 200)
  }

  // Handle clear selection
  const handleClear = () => {
    setSelectedFile(null)
    setError('')
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
