import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import { FileText, Clock, CheckCircle, XCircle, Upload, TrendingUp } from 'lucide-react'
import { getDocuments, getDocumentStats } from '../services/api'
import DocumentCard from '../components/DocumentCard'
import StatusChart from '../components/StatusChart'

export default function Dashboard() {
  const { data: documents, isLoading } = useQuery('documents', getDocuments)
  const { data: stats } = useQuery('document-stats', getDocumentStats)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-green"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Total Documents</p>
              <p className="text-2xl font-bold mt-1">{stats?.total || 0}</p>
            </div>
            <div className="p-3 bg-dark-700 rounded-lg">
              <FileText className="text-accent-green" size={24} />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Pending</p>
              <p className="text-2xl font-bold mt-1">{stats?.pending || 0}</p>
            </div>
            <div className="p-3 bg-dark-700 rounded-lg">
              <Clock className="text-accent-yellow" size={24} />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Completed</p>
              <p className="text-2xl font-bold mt-1">{stats?.completed || 0}</p>
            </div>
            <div className="p-3 bg-dark-700 rounded-lg">
              <CheckCircle className="text-accent-green" size={24} />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Failed</p>
              <p className="text-2xl font-bold mt-1">{stats?.failed || 0}</p>
            </div>
            <div className="p-3 bg-dark-700 rounded-lg">
              <XCircle className="text-accent-red" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-medium mb-4">Status Distribution</h3>
          <StatusChart data={stats} />
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-medium mb-4">Processing Overview</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Completion Rate</span>
                <span className="text-accent-green">{stats?.completionRate || 0}%</span>
              </div>
              <div className="w-full bg-dark-700 rounded-full h-2">
                <div
                  className="bg-accent-green h-2 rounded-full transition-all duration-500"
                  style={{ width: `${stats?.completionRate || 0}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="text-center">
                <p className="text-2xl font-bold text-accent-green">{stats?.successful || 0}</p>
                <p className="text-sm text-gray-400">Successful</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-accent-red">{stats?.failed || 0}</p>
                <p className="text-sm text-gray-400">Failed</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Documents */}
      <div className="card p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium">Recent Documents</h3>
          <Link to="/upload" className="btn btn-primary flex items-center gap-2">
            <Upload size={16} />
            Upload Documents
          </Link>
        </div>

        <div className="space-y-3">
          {documents?.documents.slice(0, 5).map((doc) => (
            <DocumentCard key={doc.id} document={doc} />
          ))}
        </div>

        {documents?.documents.length === 0 && (
          <div className="text-center py-12">
            <FileText className="mx-auto text-gray-600" size={48} />
            <p className="text-gray-400 mt-4">No documents uploaded yet</p>
            <Link to="/upload" className="btn btn-primary mt-4">
              Upload your first document
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}