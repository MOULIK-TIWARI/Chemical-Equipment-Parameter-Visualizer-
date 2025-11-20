import { useState, useMemo } from 'react'
import './DataTable.css'

function DataTable({ data = [] }) {
  const [currentPage, setCurrentPage] = useState(1)
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })
  const itemsPerPage = 10

  // Sorting logic
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return data

    const sorted = [...data].sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]

      // Handle numeric sorting
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue
      }

      // Handle string sorting
      const aString = String(aValue).toLowerCase()
      const bString = String(bValue).toLowerCase()

      if (aString < bString) {
        return sortConfig.direction === 'asc' ? -1 : 1
      }
      if (aString > bString) {
        return sortConfig.direction === 'asc' ? 1 : -1
      }
      return 0
    })

    return sorted
  }, [data, sortConfig])

  // Pagination logic
  const totalPages = Math.ceil(sortedData.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentData = sortedData.slice(startIndex, endIndex)

  // Handle sort
  const handleSort = (key) => {
    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }
    setSortConfig({ key, direction })
    setCurrentPage(1) // Reset to first page when sorting
  }

  // Handle page change
  const handlePageChange = (page) => {
    setCurrentPage(page)
  }

  // Get sort indicator
  const getSortIndicator = (key) => {
    if (sortConfig.key !== key) return '⇅'
    return sortConfig.direction === 'asc' ? '↑' : '↓'
  }

  if (!data || data.length === 0) {
    return (
      <div className="data-table-container">
        <h3>Equipment Data Table</h3>
        <div className="empty-table">No equipment records available</div>
      </div>
    )
  }

  return (
    <div className="data-table-container">
      <div className="table-header">
        <h3>Equipment Data Table</h3>
        <div className="table-info">
          Showing {startIndex + 1}-{Math.min(endIndex, sortedData.length)} of {sortedData.length} records
        </div>
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('equipment_name')} className="sortable">
                Equipment Name {getSortIndicator('equipment_name')}
              </th>
              <th onClick={() => handleSort('equipment_type')} className="sortable">
                Type {getSortIndicator('equipment_type')}
              </th>
              <th onClick={() => handleSort('flowrate')} className="sortable">
                Flowrate (L/min) {getSortIndicator('flowrate')}
              </th>
              <th onClick={() => handleSort('pressure')} className="sortable">
                Pressure (bar) {getSortIndicator('pressure')}
              </th>
              <th onClick={() => handleSort('temperature')} className="sortable">
                Temperature (°C) {getSortIndicator('temperature')}
              </th>
            </tr>
          </thead>
          <tbody>
            {currentData.map((record, index) => (
              <tr key={record.id || index}>
                <td>{record.equipment_name}</td>
                <td>{record.equipment_type}</td>
                <td className="numeric">{record.flowrate?.toFixed(2)}</td>
                <td className="numeric">{record.pressure?.toFixed(2)}</td>
                <td className="numeric">{record.temperature?.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination controls */}
      {totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="pagination-btn"
          >
            Previous
          </button>

          <div className="pagination-pages">
            {[...Array(totalPages)].map((_, index) => {
              const page = index + 1
              // Show first page, last page, current page, and pages around current
              if (
                page === 1 ||
                page === totalPages ||
                (page >= currentPage - 1 && page <= currentPage + 1)
              ) {
                return (
                  <button
                    key={page}
                    onClick={() => handlePageChange(page)}
                    className={`pagination-btn ${currentPage === page ? 'active' : ''}`}
                  >
                    {page}
                  </button>
                )
              } else if (page === currentPage - 2 || page === currentPage + 2) {
                return <span key={page} className="pagination-ellipsis">...</span>
              }
              return null
            })}
          </div>

          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="pagination-btn"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

export default DataTable
