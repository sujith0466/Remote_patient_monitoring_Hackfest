import React from 'react'
import { Link } from 'react-router-dom'

export default function NotFound(){
  return (
    <div className="max-w-2xl mx-auto bg-white p-6 rounded shadow text-center">
      <h2 className="text-2xl font-bold mb-2">404 — Not Found</h2>
      <p className="text-sm text-gray-600 mb-4">The page you were looking for does not exist.</p>
      <Link to="/nurse" className="text-blue-600 hover:underline">Go to Nurse Dashboard</Link>
    </div>
  )
}
