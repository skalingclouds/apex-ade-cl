import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { 
  CheckSquare, 
  Square, 
  FileText, 
  Archive,
  RotateCcw,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import toast from 'react-hot-toast'
import DocumentPreviewModal from '../components/DocumentPreviewModal'
import { DocumentStatus } from '../types/document'
import api from '../services/api'

interface Document {
  id: number
  filename: string
  status: DocumentStatus
  uploaded_at: string
  processed_at?: string
  archived: boolean
  archived_at?: string
  archived_by?: string
}

interface DocumentListResponse {
  documents: Document[]
  total: number
  page: number
  pages: number
}

type TabType = 'approved' | 'rejected' | 'escalated'

export default function DocumentManagement() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<TabType>('approved')
  const [selectedDocs, setSelectedDocs] = useState<Set<number>>(new Set())
  const [previewDocId, setPreviewDocId] = useState<number | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [includeArchived, setIncludeArchived] = useState(false)
  
  // Map tab to DocumentStatus
  const statusMap: Record<TabType, DocumentStatus> = {
    approved: DocumentStatus.APPROVED,
    rejected: DocumentStatus.REJECTED,
    escalated: DocumentStatus.ESCALATED
  }

  // Fetch documents
  const { data, isLoading } = useQuery<DocumentListResponse>(
    ['documents-by-status', activeTab, currentPage, includeArchived],
    async () => {
      const response = await api.get(`/documents/by-status`, {
        params: {
          status: statusMap[activeTab],
          page: currentPage,
          limit: 20,
          include_archived: includeArchived
        }
      })
      return response.data
    },
    {
      keepPreviousData: true,
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to load documents')
      }
    }
  )

  // Fetch stats
  const { data: stats } = useQuery(
    ['document-stats', includeArchived],
    async () => {
      const response = await api.get('/documents/stats', {
        params: { include_archived: includeArchived }
      })
      return response.data
    }
  )

  // Archive single document
  const archiveMutation = useMutation(
    async (documentId: number) => {
      await api.delete(`/documents/${documentId}/archive`)
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['documents-by-status'])
        queryClient.invalidateQueries(['document-stats'])
        toast.success('Document archived')
        setSelectedDocs(new Set())
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to archive document')
      }
    }
  )

  // Bulk archive
  const bulkArchiveMutation = useMutation(
    async (documentIds: number[]) => {
      await api.post('/documents/bulk-archive', { document_ids: documentIds })
    },
    {
      onSuccess: (_, documentIds) => {
        queryClient.invalidateQueries(['documents-by-status'])
        queryClient.invalidateQueries(['document-stats'])
        toast.success(`Archived ${documentIds.length} documents`)
        setSelectedDocs(new Set())
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to archive documents')
      }
    }
  )

  // Restore document
  const restoreMutation = useMutation(
    async (documentId: number) => {
      await api.post(`/documents/${documentId}/restore`)
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['documents-by-status'])
        queryClient.invalidateQueries(['document-stats'])
        toast.success('Document restored')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to restore document')
      }
    }
  )

  // Handle select all
  const handleSelectAll = () => {
    if (!data) return
    
    if (selectedDocs.size === data.documents.length) {
      setSelectedDocs(new Set())
    } else {
      setSelectedDocs(new Set(data.documents.map(d => d.id)))
    }
  }

  // Handle individual selection
  const handleSelectDoc = (docId: number) => {
    const newSelected = new Set(selectedDocs)
    if (newSelected.has(docId)) {
      newSelected.delete(docId)
    } else {
      newSelected.add(docId)
    }
    setSelectedDocs(newSelected)
  }

  // Handle bulk archive
  const handleBulkArchive = () => {
    if (selectedDocs.size === 0) return
    
    if (confirm(`Are you sure you want to archive ${selectedDocs.size} documents?`)) {
      bulkArchiveMutation.mutate(Array.from(selectedDocs))
    }
  }

  // Tab content with badges
  const tabs = [
    { 
      key: 'approved' as TabType, 
      label: 'Approved',
      count: stats?.stats?.APPROVED || 0,
      color: 'bg-green-500'
    },
    { 
      key: 'rejected' as TabType, 
      label: 'Rejected',
      count: stats?.stats?.REJECTED || 0,
      color: 'bg-red-500'
    },
    { 
      key: 'escalated' as TabType, 
      label: 'Escalated',
      count: stats?.stats?.ESCALATED || 0,
      color: 'bg-yellow-500'
    }
  ]

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <h1 className="text-2xl font-bold">Document Management</h1>
        <p className="text-sm text-gray-400 mt-1">
          Manage approved, rejected, and escalated documents
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => {
              setActiveTab(tab.key)
              setCurrentPage(1)
              setSelectedDocs(new Set())
            }}
            className={`px-6 py-3 font-medium transition-colors relative ${
              activeTab === tab.key
                ? 'text-white border-b-2 border-accent-blue'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className={`ml-2 px-2 py-0.5 text-xs rounded-full text-white ${tab.color}`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
        
        {/* Archived toggle */}
        <div className="ml-auto flex items-center px-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={includeArchived}
              onChange={(e) => {
                setIncludeArchived(e.target.checked)
                setCurrentPage(1)
              }}
              className="rounded border-gray-600 bg-dark-700"
            />
            Show archived
            {includeArchived && stats?.stats?.ARCHIVED && (
              <span className="px-2 py-0.5 text-xs rounded-full bg-gray-600 text-white">
                {stats.stats.ARCHIVED}
              </span>
            )}
          </label>
        </div>
      </div>

      {/* Toolbar */}
      {selectedDocs.size > 0 && (
        <div className="px-6 py-3 bg-dark-700 flex items-center gap-4">
          <span className="text-sm">
            {selectedDocs.size} selected
          </span>
          <button
            onClick={handleBulkArchive}
            className="btn-secondary text-sm flex items-center gap-2"
          >
            <Archive size={16} />
            Archive Selected
          </button>
          <button
            onClick={() => setSelectedDocs(new Set())}
            className="text-sm text-gray-400 hover:text-white"
          >
            Clear Selection
          </button>
        </div>
      )}

      {/* Document List */}
      <div className="flex-1 overflow-auto p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-blue"></div>
          </div>
        ) : data && data.documents.length > 0 ? (
          <div className="space-y-2">
            {/* Select All */}
            <div className="flex items-center gap-3 p-3 bg-dark-700 rounded-lg">
              <button
                onClick={handleSelectAll}
                className="hover:text-accent-blue"
              >
                {selectedDocs.size === data.documents.length ? (
                  <CheckSquare size={20} />
                ) : (
                  <Square size={20} />
                )}
              </button>
              <span className="text-sm font-medium">Select All</span>
            </div>

            {/* Document Items */}
            {data.documents.map(doc => (
              <div
                key={doc.id}
                className={`flex items-center gap-3 p-4 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors ${
                  doc.archived ? 'opacity-60' : ''
                }`}
              >
                <button
                  onClick={() => handleSelectDoc(doc.id)}
                  className="hover:text-accent-blue"
                >
                  {selectedDocs.has(doc.id) ? (
                    <CheckSquare size={20} />
                  ) : (
                    <Square size={20} />
                  )}
                </button>
                
                <FileText size={20} className="text-gray-400" />
                
                <button
                  onClick={() => setPreviewDocId(doc.id)}
                  className="flex-1 text-left hover:text-accent-blue transition-colors"
                >
                  <div className="font-medium">{doc.filename}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    Uploaded: {new Date(doc.uploaded_at).toLocaleDateString()}
                    {doc.processed_at && ` • Processed: ${new Date(doc.processed_at).toLocaleDateString()}`}
                    {doc.archived && doc.archived_at && ` • Archived: ${new Date(doc.archived_at).toLocaleDateString()}`}
                  </div>
                </button>
                
                <div className="flex items-center gap-2">
                  {doc.archived ? (
                    <button
                      onClick={() => restoreMutation.mutate(doc.id)}
                      className="p-2 hover:bg-dark-600 rounded transition-colors"
                      title="Restore"
                    >
                      <RotateCcw size={16} />
                    </button>
                  ) : (
                    <button
                      onClick={() => archiveMutation.mutate(doc.id)}
                      className="p-2 hover:bg-dark-600 rounded transition-colors"
                      title="Archive"
                    >
                      <Archive size={16} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <Archive size={48} className="mb-4" />
            <p>No {activeTab} documents found</p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="px-6 py-4 border-t border-gray-700 flex items-center justify-between">
          <div className="text-sm text-gray-400">
            Page {data.page} of {data.pages} • Total: {data.total} documents
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-2 hover:bg-dark-700 rounded disabled:opacity-50"
            >
              <ChevronLeft size={16} />
            </button>
            <span className="px-3 py-1 bg-dark-700 rounded">
              {currentPage}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(data.pages, p + 1))}
              disabled={currentPage === data.pages}
              className="p-2 hover:bg-dark-700 rounded disabled:opacity-50"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {previewDocId && (
        <DocumentPreviewModal
          documentId={previewDocId}
          onClose={() => setPreviewDocId(null)}
        />
      )}
    </div>
  )
}