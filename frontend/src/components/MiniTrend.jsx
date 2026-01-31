import React from 'react'
import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip)

export default function MiniTrend({ labels = [], data = [], color = '#3b82f6' }){
  const chartData = {
    labels,
    datasets: [
      {
        data,
        borderColor: color,
        backgroundColor: 'transparent',
        pointRadius: 0,
        borderWidth: 2,
        tension: 0.3
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { display: false },
      y: { display: false }
    },
    plugins: { tooltip: { enabled: false }, legend: { display: false } }
  }

  return (
    <div style={{ width: 100, height: 40 }}>
      <Line data={chartData} options={options} />
    </div>
  )
}
