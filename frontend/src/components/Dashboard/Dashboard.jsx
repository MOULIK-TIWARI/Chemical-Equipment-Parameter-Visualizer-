import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import api from '../../services/api'
import SummaryStats from './SummaryStats'
import DataTable from './DataTable'
import Charts from './Charts'
import FileUpload from '../Upload/FileUpload'
import PDFDownload from '../Reports/PDFDownload'
import { logout } from '../../utils/auth'
import './Dashboard.css'

function Dashboard() {
  const location = useLocation()
  const navigate = useNavigate()
  
  const [dataset, setDataset] = useState(null)
  const [datasetData, setDatasetData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showUpload, setShowUpload] = useState(false)

  // Fetch current dataset on mount
  useEffect(() => {
    fetchCurrentDataset()
  }, [location.state])

  const fetchCurrentDataset = async () => {
    setLoading(true)
    setError('')

    try {
      // Check if we have a specific dataset ID from navigation state
      const datasetId = location.state?.datasetId

      if (datasetId) {
        // Fetch specific dataset
        await fetchDatasetById(datasetId)
      } else {
        // Fetch the most recent dataset
        await fetchMostRecentDataset()
      }
    } catch (err) {
      setError(err.message || 'Failed to load dataset')
      setLoading(false)
    }
  }

  const fetchDatasetById = async (id) => {
    try {
      // Fetch dataset summary
      const summaryResponse = await api.get(`/datasets/${id}/summary/`)
      setDataset(summaryResponse.data)

      // Fetch dataset records
      const dataResponse = await api.get(`/datasets/${id}/data/`)
      setDatasetData(dataResponse.data.results || [])

      setLoading(false)
    } catch (err) {
      throw err
    }
  }

  const fetchMostRecentDataset = async () => {
    try {
      // Fetch list of datasets (last 5)
      const response = await api.get('/datasets/')
      
      if (response.data && response.data.length > 0) {
        // Get the most recent dataset (first in the list)
        const mostRecent = response.data[0]
        await fetchDatasetById(mostRecent.id)
      } else {
        // No datasets available
        setDataset(null)
        setDatasetData([])
        setLoading(false)
      }
    } catch (err) {
      throw err
    }
  }

  const handleUploadSuccess = () => {
    // Refresh dashboard with newly uploaded dataset
    setDataset(null)
    setDatasetData([])
    setShowUpload(false)
    fetchCurrentDataset()
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleViewHistory = () => {
    navigate('/history')
  }

  const handleNewUpload = () => {
    setShowUpload(true)
  }

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading dashboard...</div>
      </div>
    )
  }

  if (showUpload) {
    return (
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Chemical Equipment Analytics</h1>
          <div className="header-actions">
            <button onClick={() => setShowUpload(false)} className="btn-secondary">
              Back to Dashboard
            </button>
            <button onClick={handleViewHistory} className="btn-secondary">
              View History
            </button>
            <button onClick={handleLogout} className="btn-logout">
              Logout
            </button>
          </div>
        </div>
        <FileUpload onUploadSuccess={handleUploadSuccess} />
      </div>
    )
  }

  return (
    <div className="dashboard-container">
      {/* Header section */}
      <div className="dashboard-header">
        <h1>Chemical Equipment Analytics</h1>
        <div className="header-actions">
          <button onClick={handleNewUpload} className="btn-primary">
            Upload New Dataset
          </button>
          <button onClick={handleViewHistory} className="btn-secondary">
            View History
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

      {/* Main content */}
      {dataset ? (
        <div className="dashboard-content">
          {/* Dataset info */}
          <div className="dataset-info">
            <h2>{dataset.name}</h2>
            <p className="dataset-meta">
              Uploaded: {new Date(dataset.uploaded_at).toLocaleString()} | 
              Total Records: {dataset.total_records}
            </p>
          </div>

          {/* PDF Download section */}
          <section className="dashboard-section">
            <PDFDownload datasetId={dataset.id} datasetName={dataset.name} />
          </section>

          {/* Summary statistics section */}
          <section className="dashboard-section">
            <SummaryStats dataset={dataset} />
          </section>

          {/* Charts section */}
          <section className="dashboard-section">
            <Charts dataset={dataset} />
          </section>

          {/* Data table section */}
          <section className="dashboard-section">
            <DataTable data={datasetData} datasetId={dataset.id} />
          </section>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-state-icon">📊</div>
          <h2>No Data Available</h2>
          <p>Upload a CSV file to get started with equipment analytics</p>
          <button onClick={handleNewUpload} className="btn-primary">
            Upload Dataset
          </button>
        </div>
      )}
    </div>
  )
}

export default Dashboard
