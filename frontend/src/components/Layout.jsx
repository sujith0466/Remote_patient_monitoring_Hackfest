import React from 'react'

export default function Layout({ children, role }){
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-4 text-sm text-gray-700">Role: <span className="font-medium">{role}</span></div>
      {children}
    </div>
  )
}
