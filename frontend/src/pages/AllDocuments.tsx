import { useState } from 'react'
import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Loader,
  Search,
  Filter
} from 'lucide-react'
import { getDocuments } from '../services/api'
import { formatDistanceToNow } from '../utils/date'

export default function AllDocuments() {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  
  const { data, isLoading } = useQuery('all-documents', getDocuments)

  const statusConfig = {
    pending: { icon: Clock, color: 'text-gray-400', bg: 'bg-gray-400/10' },
    parsing: { icon: Clock, color: 'text-accent-yellow', bg: 'bg-accent-yellow/10' },
    parsed: { icon: Clock, color: 'text-accent-yellow', bg: 'bg-accent-yellow/10' },
    extracting: { icon: Clock, color: 'text-accent-yellow', bg: 'bg-accent-yellow/10' },
    extracted: { icon: CheckCircle, color: 'text-accent-green', bg: 'bg-accent-green/10' },
    approved: { icon: CheckCircle, color: 'text-accent-green', bg: 'bg-accent-green/10' },
    rejected: { icon: XCircle, color: 'text-accent-red', bg: 'bg-accent-red/10' },
    escalated: { icon: AlertTriangle, color: 'text-accent-yellow', bg: 'bg-accent-yellow/10' },
    failed: { icon: XCircle, color: 'text-accent-red', bg: 'bg-accent-red/10' },
  }

  const filteredDocuments = data?.documents.filter(doc => {
    const matchesSearch = doc.filename.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || doc.status.toLowerCase() === statusFilter.toLowerCase()
    return matchesSearch && matchesStatus
  }) || []

  const statusCounts = data?.documents.reduce((acc, doc) => {
    const status = doc.status.toLowerCase()
    acc[status] = (acc[status] || 0) + 1
    return acc
  }, {} as Record<string, number>) || {}

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader className="animate-spin" size={48} />
      </div>
    )
  }

  return (
    <div className="p-6 h-full flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-4">All Documents</h1>
        
        {/* Search and Filter Bar */}
        <div className="flex gap-4 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-dark-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-green"
            />
          </div>
          
          <div className="flex items-center gap-2">
            <Filter className="text-gray-400" size={20} />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-dark-700 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-green"
            >
              <option value="all">All Status ({data?.documents.length || 0})</option>
              {Object.entries(statusCounts).map(([status, count]) => (
                <option key={status} value={status}>
                  {status.charAt(0).toUpperCase() + status.slice(1)} ({count})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Status Summary */}
        <div className="grid grid-cols-6 gap-2">
          {Object.entries(statusCounts).map(([status, count]) => {
            const config = statusConfig[status as keyof typeof statusConfig]
            if (!config) return null
            const Icon = config.icon
            return (
              <div key={status} className="bg-dark-700 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Icon size={16} className={config.color} />
                  <span className="text-xs text-gray-400 capitalize">{status}</span>
                </div>
                <div className="text-xl font-bold">{count}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-auto">
        {filteredDocuments.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <FileText size={48} className="mb-4" />
            <p>No documents found</p>
          </div>
        ) : (
          <div className="grid gap-3">
            {filteredDocuments.map(doc => {
              const normalizedStatus = doc.status.toLowerCase()
              const config = statusConfig[normalizedStatus as keyof typeof statusConfig] || statusConfig.pending
              const StatusIcon = config.icon
              
              return (
                <Link
                  key={doc.id}
                  to={`/documents/${doc.id}`}
                  className="bg-dark-700 hover:bg-dark-600 rounded-lg p-4 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`p-3 rounded-lg ${config.bg}`}>
                        <StatusIcon className={config.color} size={24} />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg">{doc.filename}</h3>
                        <p className="text-sm text-gray-400">
                          Uploaded {formatDistanceToNow(doc.uploaded_at)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.color}`}>
                        {doc.status}
                      </span>
                      {doc.processed_at && (
                        <p className="text-xs text-gray-500 mt-2">
                          Processed {formatDistanceToNow(doc.processed_at)}
                        </p>
                      )}
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}