import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery } from 'react-query'
import { 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Clock,
  Loader,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { getDocuments, Document } from '../services/api'

interface DocumentSidebarProps {
  isOpen: boolean
  onToggle: () => void
}

const statusIcons = {
  pending: <Clock size={16} className="text-gray-400" />,
  parsing: <Loader size={16} className="text-blue-400 animate-spin" />,
  parsed: <FileText size={16} className="text-blue-400" />,
  extracting: <Loader size={16} className="text-yellow-400 animate-spin" />,
  extracted: <FileText size={16} className="text-yellow-400" />,
  approved: <CheckCircle size={16} className="text-green-400" />,
  rejected: <XCircle size={16} className="text-red-400" />,
  escalated: <AlertTriangle size={16} className="text-orange-400" />,
  failed: <XCircle size={16} className="text-red-600" />
}

const statusColors = {
  pending: 'text-gray-400',
  parsing: 'text-blue-400',
  parsed: 'text-blue-400',
  extracting: 'text-yellow-400',
  extracted: 'text-yellow-400',
  approved: 'text-green-400',
  rejected: 'text-red-400',
  escalated: 'text-orange-400',
  failed: 'text-red-600'
}

export default function DocumentSidebar({ isOpen, onToggle }: DocumentSidebarProps) {
  const navigate = useNavigate()
  const { id: currentDocId } = useParams<{ id: string }>()
  const currentDocumentId = currentDocId ? parseInt(currentDocId) : null

  const { data, isLoading, refetch } = useQuery(
    'sidebar-documents',
    () => getDocuments(),
    {
      refetchInterval: 5000, // Poll every 5 seconds for status updates
    }
  )

  const handleDocumentClick = (docId: number) => {
    navigate(`/documents/${docId}`)
  }

  return (
    <div className={`relative transition-all duration-300 ${isOpen ? 'w-80' : 'w-0'}`}>
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="absolute -right-10 top-4 p-2 bg-dark-800 hover:bg-dark-700 rounded-r-lg transition-colors z-10"
        title={isOpen ? 'Close sidebar' : 'Open sidebar'}
      >
        {isOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
      </button>

      {/* Sidebar Content */}
      {isOpen && (
        <div className="h-full bg-dark-800 border-r border-dark-600 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-dark-600">
            <h2 className="font-semibold text-lg">Documents</h2>
            <p className="text-sm text-gray-400 mt-1">
              {data?.documents.length || 0} total documents
            </p>
          </div>

          {/* Document List */}
          <div className="flex-1 overflow-y-auto p-2">
            {isLoading ? (
              <div className="flex items-center justify-center p-8">
                <Loader className="animate-spin" size={24} />
              </div>
            ) : (
              <div className="space-y-1">
                {data?.documents.map((doc) => (
                  <button
                    key={doc.id}
                    onClick={() => handleDocumentClick(doc.id)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      currentDocumentId === doc.id
                        ? 'bg-dark-700 border border-dark-500'
                        : 'hover:bg-dark-700'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5">
                        {statusIcons[doc.status]}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{doc.filename}</p>
                        <p className={`text-sm ${statusColors[doc.status]} capitalize`}>
                          {doc.status}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(doc.uploaded_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
                
                {data?.documents.length === 0 && (
                  <div className="text-center p-8 text-gray-400">
                    <FileText size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No documents found</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Status Summary */}
          {data && data.documents.length > 0 && (
            <div className="p-4 border-t border-dark-600">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-gray-400">Pending:</span>
                  <span className="ml-2 font-medium">
                    {data.documents.filter(d => ['pending', 'parsing', 'extracting'].includes(d.status)).length}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Approved:</span>
                  <span className="ml-2 font-medium text-green-400">
                    {data.documents.filter(d => d.status === 'APPROVED').length}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Rejected:</span>
                  <span className="ml-2 font-medium text-red-400">
                    {data.documents.filter(d => d.status === 'REJECTED').length}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Failed:</span>
                  <span className="ml-2 font-medium text-red-600">
                    {data.documents.filter(d => d.status === 'FAILED').length}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}