import { Link, useLocation } from 'react-router-dom'
import DevAuth from './DevAuth'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext' // Import useTheme

export default function Header(){
  const { isAuthenticated, user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme(); // Use theme context
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';

  return (
    <header className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <h1 className="text-xl font-bold dark:text-white">CareWatch</h1>
        {!isLoginPage && (
          <nav className="space-x-4">
            {isAuthenticated && user && (
              <>
                {user.role === 'nurse' && (
                  <Link to="/nurse" className="text-blue-600 hover:underline dark:text-blue-400">Nurse Dashboard</Link>
                )}
                {user.role === 'doctor' && (
                  <Link to="/doctor" className="text-blue-600 hover:underline dark:text-blue-400">Doctor Dashboard</Link>
                )}
                {/* If a user has both roles or we want to show both, we can adjust here */}
                {/* For now, only show the link relevant to their primary role */}
              </>
            )}
          </nav>
        )}
        <div className="flex items-center space-x-4">
          {!isLoginPage && <DevAuth />}
          {!isLoginPage && isAuthenticated && (
            <button
              onClick={logout}
              className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
            >
              Logout
            </button>
          )}
          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </div>
    </header>
  )
}
