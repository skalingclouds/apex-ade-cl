import { Outlet, NavLink } from 'react-router-dom'
import { FileText, Upload, LayoutDashboard, Sun, Moon, BarChart3, Archive } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

export default function Layout() {
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-dark-800 dark:bg-dark-800 bg-white border-r border-dark-600 dark:border-dark-600 border-gray-200">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-accent-green">Apex ADE</h1>
          <p className="text-sm text-gray-400 mt-1">Advanced Document Extraction</p>
        </div>
        
        <nav className="px-4 pb-6">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-dark-700 text-white'
                  : 'text-gray-400 hover:bg-dark-700 hover:text-white'
              }`
            }
          >
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </NavLink>
          
          <NavLink
            to="/upload"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors mt-2 ${
                isActive
                  ? 'bg-dark-700 text-white'
                  : 'text-gray-400 hover:bg-dark-700 hover:text-white'
              }`
            }
          >
            <Upload size={20} />
            <span>Upload Documents</span>
          </NavLink>
          
          <NavLink
            to="/documents"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors mt-2 ${
                isActive
                  ? 'bg-dark-700 text-white'
                  : 'text-gray-400 hover:bg-dark-700 hover:text-white'
              }`
            }
          >
            <FileText size={20} />
            <span>All Documents</span>
          </NavLink>
          
          <NavLink
            to="/document-management"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors mt-2 ${
                isActive
                  ? 'bg-dark-700 text-white'
                  : 'text-gray-400 hover:bg-dark-700 hover:text-white'
              }`
            }
          >
            <Archive size={20} />
            <span>Document Management</span>
          </NavLink>
          
          <NavLink
            to="/analytics"
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors mt-2 ${
                isActive
                  ? 'bg-dark-700 text-white'
                  : 'text-gray-400 hover:bg-dark-700 hover:text-white'
              }`
            }
          >
            <BarChart3 size={20} />
            <span>Analytics</span>
          </NavLink>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 bg-dark-800 border-b border-dark-600 flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-medium">ADE Dashboard</h2>
            <span className="text-sm text-gray-400">
              Monitor and manage your document processing workflow
            </span>
          </div>
          
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-dark-700 dark:hover:bg-dark-700 hover:bg-gray-200 transition-colors"
            title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? <Sun size={20} className="text-yellow-400" /> : <Moon size={20} className="text-blue-600" />}
          </button>
        </header>

        {/* Page Content */}
        <main className="flex-1 bg-dark-900 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}