import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import NurseDashboard from './pages/NurseDashboard'
import DoctorDashboard from './pages/DoctorDashboard'
import NotFound from './pages/NotFound'
import Header from './components/Header'

export default function App(){
  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="p-4">
        <Routes>
          <Route path="/" element={<Navigate to="/nurse" replace />} />
          <Route path="/nurse" element={<NurseDashboard />} />
          <Route path="/doctor" element={<DoctorDashboard />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
  )
}
