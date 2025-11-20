import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import './Charts.css'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

function Charts({ dataset }) {
  if (!dataset) {
    return null
  }

  // Prepare data for equipment type distribution chart
  const typeDistribution = dataset.type_distribution || {}
  const typeLabels = Object.keys(typeDistribution)
  const typeCounts = Object.values(typeDistribution)

  const typeDistributionData = {
    labels: typeLabels,
    datasets: [
      {
        label: 'Equipment Count',
        data: typeCounts,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }
    ]
  }

  const typeDistributionOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      },
      title: {
        display: true,
        text: 'Equipment Type Distribution',
        font: {
          size: 16,
          weight: 'bold'
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1
        },
        title: {
          display: true,
          text: 'Count'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Equipment Type'
        }
      }
    }
  }

  // Prepare data for average values chart
  const averageLabels = ['Flowrate (L/min)', 'Pressure (bar)', 'Temperature (°C)']
  const averageValues = [
    dataset.avg_flowrate || 0,
    dataset.avg_pressure || 0,
    dataset.avg_temperature || 0
  ]

  const averageValuesData = {
    labels: averageLabels,
    datasets: [
      {
        label: 'Average Value',
        data: averageValues,
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 159, 64, 0.6)',
          'rgba(255, 99, 132, 0.6)'
        ],
        borderColor: [
          'rgba(75, 192, 192, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(255, 99, 132, 1)'
        ],
        borderWidth: 1
      }
    ]
  }

  const averageValuesOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: 'Average Values',
        font: {
          size: 16,
          weight: 'bold'
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Value'
        }
      }
    }
  }

  return (
    <div className="charts-container">
      <h3>Data Visualizations</h3>
      <div className="charts-grid">
        {/* Equipment Type Distribution Chart */}
        <div className="chart-wrapper">
          <Bar data={typeDistributionData} options={typeDistributionOptions} />
        </div>

        {/* Average Values Chart */}
        <div className="chart-wrapper">
          <Bar data={averageValuesData} options={averageValuesOptions} />
        </div>
      </div>
    </div>
  )
}

export default Charts
