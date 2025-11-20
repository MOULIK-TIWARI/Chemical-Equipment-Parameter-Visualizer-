import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../services/api'
import { logout } from '../../utils/auth'
import './DatasetHistory.css'

function DatasetHistory() {
  const navigate = useNavigate()
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Fetch list of datasets on mount
  useEffect(() => {
    fetchDatasets()
  }, [])

  const fetchDatasets = async () => {
    setLoading(true)
    setError('')

    try {
      // Fetch list of last 5 datasets
      const response = await api.get('/datasets/')
      setDatasets(response.data || [])
      setLoading(false)
    } catch (err) {
      setError(err.message || 'Failed to load dataset history')
      setLoading(false)
    }
  }

  const handleDatasetClick = (datasetId) => {
    // Navigate to dashboard with selected dataset
    navigate('/dashboard', { state: { datasetId } })
  }

  const handleBackToDashboard = () => {
    navigate('/dashboard')
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="history-container">
        <div className="loading">Loading dataset history...</div>
      </div>
    )
  }

  return (
    <div className="history-container">
      {/* Header section */}
      <div className="history-header">
        <h1>Dataset History</h1>
        <div className="header-actions">
          <button onClick={handleBackToDashboard} className="btn-secondary">
            Back to Dashboard
          </button>
          <button onClick={handleLogout} className="btn-logout">
            Logout
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {/* Dataset list */}
      {datasets.length > 0 ? (
        <div className="datasets-grid">
          {datasets.map((dataset) => (
            <div 
              key={dataset.id} 
              className="dataset-card"
              onClick={() => handleDatasetClick(dataset.id)}
            >
              <div className="dataset-card-header">
                <h3>{dataset.name}</h3>
                <span className="dataset-id">ID: {dataset.id}</span>
              </div>
              
              <div className="dataset-card-body">
                <div className="dataset-meta">
                  <div className="meta-item">
                    <span className="meta-icon">📅</span>
                    <span className="meta-text">
                      {new Date(dataset.uploaded_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-icon">🕒</span>
                    <span className="meta-text">
                      {new Date(dataset.uploaded_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>

                <div className="dataset-summary">
                  <div className="summary-item">
                    <span className="summary-label">Total Records</span>
                    <span className="summary-value">{dataset.total_records}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Avg Flowrate</span>
                    <span className="summary-value">{dataset.avg_flowrate?.toFixed(2)} L/min</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Avg Pressure</span>
                    <span className="summary-value">{dataset.avg_pressure?.toFixed(2)} bar</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Avg Temperature</span>
                    <span className="summary-value">{dataset.avg_temperature?.toFixed(2)} °C</span>
                  </div>
                </div>

                {dataset.type_distribution && (
                  <div className="type-distribution">
                    <span className="distribution-label">Equipment Types:</span>
                    <div className="distribution-tags">
                      {Object.entries(dataset.type_distribution).map(([type, count]) => (
                        <span key={type} className="type-tag">
                          {type} ({count})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="dataset-card-footer">
                <span className="view-details">Click to view details →</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-state-icon">📂</div>
          <h2>No Datasets Found</h2>
          <p>Upload a CSV file to create your first dataset</p>
          <button onClick={handleBackToDashboard} className="btn-primary">
            Go to Dashboard
          </button>
        </div>
      )}
    </div>
  )
}

export default DatasetHistory
