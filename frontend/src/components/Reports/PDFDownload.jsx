import { useState } from 'react'
import api from '../../services/api'
import { useToast } from '../Toast/ToastContainer'
import './PDFDownload.css'

function PDFDownload({ datasetId, datasetName }) {
  const toast = useToast()
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState('')

  const handleDownload = async () => {
    if (!datasetId) {
      const errorMsg = 'No dataset selected'
      setError(errorMsg)
      toast.showError(errorMsg)
      return
    }

    setDownloading(true)
    setError('')

    try {
      // Call GET /api/datasets/{id}/report/ endpoint
      const response = await api.get(`/datasets/${datasetId}/report/`, {
        responseType: 'blob', // Important for file download
      })

      // Create a blob from the response
      const blob = new Blob([response.data], { type: 'application/pdf' })

      // Create a temporary URL for the blob
      const url = window.URL.createObjectURL(blob)

      // Create a temporary anchor element to trigger download
      const link = document.createElement('a')
      link.href = url
      link.download = `${datasetName || 'report'}_${datasetId}.pdf`
      
      // Append to body, click, and remove
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      // Clean up the temporary URL
      window.URL.revokeObjectURL(url)

      setDownloading(false)
      toast.showSuccess('PDF report downloaded successfully!')
    } catch (err) {
      const errorMsg = err.message || 'Failed to download PDF report'
      setError(errorMsg)
      toast.showError(errorMsg)
      setDownloading(false)
    }
  }

  return (
    <div className="pdf-download">
      <h3 className="pdf-download-title">PDF Report</h3>
      <button 
        onClick={handleDownload} 
        disabled={downloading || !datasetId}
        className={`btn-primary pdf-download-btn ${downloading ? 'downloading' : ''}`}
      >
        {downloading ? (
          <>
            <span className="spinner"></span>
            <span>Generating PDF...</span>
          </>
        ) : (
          <>
            <span>📥</span>
            <span>Download PDF Report</span>
          </>
        )}
      </button>
      {error && (
        <div className="pdf-download-error">
          {error}
        </div>
      )}
    </div>
  )
}

export default PDFDownload
