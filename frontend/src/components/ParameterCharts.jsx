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

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

function SmallChart({ labels, data, label, color }){
  const chartData = {
    labels,
    datasets: [{ label, data, borderColor: color, backgroundColor: 'rgba(0,0,0,0)', tension: 0.2 }]
  }
  const options = {
    plugins: { legend: { display: false }, title: { display: false } },
    responsive: true,
    maintainAspectRatio: false,
    scales: { x: { display: true }, y: { display: true } }
  }
  return (
    <div className="bg-white p-3 rounded shadow h-48">
      <div className="text-sm font-semibold mb-2">{label}</div>
      <div style={{ height: 110 }}>
        <Line data={chartData} options={options} />
      </div>
    </div>
  )
}

export default function ParameterCharts({ data }){
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
      <SmallChart labels={data.timestamps} data={data.heartRate} label="Heart Rate (bpm)" color="#ef4444" />
      <SmallChart labels={data.timestamps} data={data.temperature} label="Temperature (°C)" color="#f59e0b" />
      <SmallChart labels={data.timestamps} data={data.spo2} label="SpO₂ (%)" color="#10b981" />
    </div>
  )
}
