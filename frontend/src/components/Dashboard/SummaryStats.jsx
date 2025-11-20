import './SummaryStats.css'

function SummaryStats({ dataset }) {
  if (!dataset) {
    return null
  }

  // Format numbers with appropriate precision
  const formatNumber = (value, decimals = 2) => {
    if (value === null || value === undefined) {
      return 'N/A'
    }
    return Number(value).toFixed(decimals)
  }

  return (
    <div className="summary-stats">
      <h3>Summary Statistics</h3>
      <div className="stats-grid">
        {/* Total Records Card */}
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-label">Total Records</div>
            <div className="stat-value">{dataset.total_records || 0}</div>
          </div>
        </div>

        {/* Average Flowrate Card */}
        <div className="stat-card">
          <div className="stat-icon">💧</div>
          <div className="stat-content">
            <div className="stat-label">Average Flowrate</div>
            <div className="stat-value">{formatNumber(dataset.avg_flowrate)}</div>
            <div className="stat-unit">L/min</div>
          </div>
        </div>

        {/* Average Pressure Card */}
        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <div className="stat-label">Average Pressure</div>
            <div className="stat-value">{formatNumber(dataset.avg_pressure)}</div>
            <div className="stat-unit">bar</div>
          </div>
        </div>

        {/* Average Temperature Card */}
        <div className="stat-card">
          <div className="stat-icon">🌡️</div>
          <div className="stat-content">
            <div className="stat-label">Average Temperature</div>
            <div className="stat-value">{formatNumber(dataset.avg_temperature)}</div>
            <div className="stat-unit">°C</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SummaryStats
