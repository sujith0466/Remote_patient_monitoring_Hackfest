import React from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export default function VitalsChart({ data }){
  const labels = data.timestamps
  const chartData = {
    labels,
    datasets: [
      {
        label: 'Heart Rate (bpm)',
        data: data.heartRate,
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239,68,68,0.15)'
      },
      {
        label: 'Temperature (°C)',
        data: data.temperature,
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245,158,11,0.12)'
      },
      {
        label: 'SpO₂ (%)',
        data: data.spo2,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16,185,129,0.12)'
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' }
    }
  }

  return (
    <div style={{ height: 320 }}>
      <Line data={chartData} options={options} />
    </div>
  )
}
