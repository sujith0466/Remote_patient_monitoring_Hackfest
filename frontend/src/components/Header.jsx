import React from 'react'
import { Link } from 'react-router-dom'
import DevAuth from './DevAuth'

export default function Header(){
  return (
    <header className="bg-white border-b">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold">CareWatch</h1>
        <nav className="space-x-4">
          <Link to="/nurse" className="text-blue-600 hover:underline">Nurse Dashboard</Link>
          <Link to="/doctor" className="text-blue-600 hover:underline">Doctor Dashboard</Link>
        </nav>
        <div>
          <DevAuth />
        </div>
      </div>
    </header>
  )
}
