import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import toast from 'react-hot-toast'
import PDFViewer from '../components/PDFViewer'
import { 
  ChevronLeft, 
  Download, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  MessageSquare,
  Loader,
  FileText
} from 'lucide-react'
import {
  getDocument,
  getDocumentPdf,
  approveDocument,
  rejectDocument,
  escalateDocument,
  parseDocument,
  extractDocument,
  exportDocumentCsv,
  exportDocumentMarkdown,
  exportDocumentText,
  getDocumentMarkdown,
  retryExtraction,
  FieldInfo
} from '../services/api'
import Chat from '../components/Chat'
import FieldSelector from '../components/FieldSelector'
import ErrorDisplay from '../components/ErrorDisplay'
import DocumentSidebar from '../components/DocumentSidebar'

export default function DocumentReview() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const [showChat, setShowChat] = useState(false)
  const [showFieldSelector, setShowFieldSelector] = useState(false)
  const [showSidebar, setShowSidebar] = useState(true)
  const [highlightAreas, setHighlightAreas] = useState<Array<{ page: number; bbox: number[] }>>([])
  const [exportingCsv, setExportingCsv] = useState(false)
  const [exportingMarkdown, setExportingMarkdown] = useState(false)
  const [exportingText, setExportingText] = useState(false)
  
  const documentId = parseInt(id!)

  const { data: document, isLoading } = useQuery(
    ['document', documentId],
    () => getDocument(documentId),
    {
      refetchInterval: (data) => {
        // Poll while processing
        if (data && ['PARSING', 'EXTRACTING'].includes(data.status)) {
          return 2000
        }
        return false
      },
    }
  )

  const { data: markdownData } = useQuery(
    ['document-markdown', documentId],
    () => getDocumentMarkdown(documentId),
    {
      enabled: !!document && ['EXTRACTED', 'APPROVED'].includes(document.status),
    }
  )

  const approveMutation = useMutation(() => approveDocument(documentId), {
    onSuccess: () => {
      queryClient.invalidateQueries(['document', documentId])
      toast.success('Document approved successfully')
    },
  })

  const rejectMutation = useMutation((reason?: string) => rejectDocument(documentId, reason), {
    onSuccess: () => {
      queryClient.invalidateQueries(['document', documentId])
      toast.success('Document rejected')
    },
  })

  const escalateMutation = useMutation((reason?: string) => escalateDocument(documentId, reason), {
    onSuccess: () => {
      queryClient.invalidateQueries(['document', documentId])
      toast.success('Document escalated for review')
    },
  })

  const parseMutation = useMutation(() => parseDocument(documentId), {
    onSuccess: () => {
      queryClient.invalidateQueries(['document', documentId])
      setShowFieldSelector(true)
    },
    onError: (error: any) => {
      queryClient.invalidateQueries(['document', documentId])
      const errorInfo = error.errorInfo || { message: error.message }
      toast.error(errorInfo.message)
    }
  })

  const extractMutation = useMutation(
    ({ selectedFields, customFields }: { selectedFields: string[], customFields?: FieldInfo[] }) => 
      extractDocument(documentId, selectedFields, customFields),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['document', documentId])
        setShowFieldSelector(false)
        toast.success('Document extracted successfully')
      },
      onError: (error: any) => {
        queryClient.invalidateQueries(['document', documentId])
        const errorInfo = error.errorInfo || { message: error.message }
        toast.error(errorInfo.message)
      }
    }
  )

  const retryMutation = useMutation(() => retryExtraction(documentId), {
    onSuccess: () => {
      queryClient.invalidateQueries(['document', documentId])
      toast.success('Retry successful')
    },
    onError: (error: any) => {
      queryClient.invalidateQueries(['document', documentId])
      const errorInfo = error.errorInfo || { message: error.message }
      toast.error(errorInfo.message)
    }
  })

  const handleExportCsv = async (retryCount = 0) => {
    setExportingCsv(true)
    try {
      const blob = await exportDocumentCsv(documentId)
      const url = window.URL.createObjectURL(blob)
      const a = window.document.createElement('a')
      a.href = url
      a.download = `${document?.filename.replace('.pdf', '')}_export.csv`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('CSV exported successfully')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to export CSV'
      
      if (retryCount < 2) {
        // Show retry option
        toast.error(
          <div>
            <p>{message}</p>
            <button 
              onClick={() => handleExportCsv(retryCount + 1)}
              className="mt-2 text-xs underline hover:text-accent-blue"
            >
              Retry
            </button>
          </div>,
          { duration: 5000 }
        )
      } else {
        toast.error(`${message} (after ${retryCount + 1} attempts)`)
      }
    } finally {
      setExportingCsv(false)
    }
  }

  const handleExportMarkdown = async (retryCount = 0) => {
    setExportingMarkdown(true)
    try {
      const blob = await exportDocumentMarkdown(documentId)
      const url = window.URL.createObjectURL(blob)
      const a = window.document.createElement('a')
      a.href = url
      a.download = `${document?.filename.replace('.pdf', '')}_export.md`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Markdown exported successfully')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to export Markdown'
      
      if (retryCount < 2) {
        // Show retry option
        toast.error(
          <div>
            <p>{message}</p>
            <button 
              onClick={() => handleExportMarkdown(retryCount + 1)}
              className="mt-2 text-xs underline hover:text-accent-blue"
            >
              Retry
            </button>
          </div>,
          { duration: 5000 }
        )
      } else {
        toast.error(`${message} (after ${retryCount + 1} attempts)`)
      }
    } finally {
      setExportingMarkdown(false)
    }
  }

  const handleExportText = async (retryCount = 0) => {
    setExportingText(true)
    try {
      const blob = await exportDocumentText(documentId)
      const url = window.URL.createObjectURL(blob)
      const a = window.document.createElement('a')
      a.href = url
      a.download = `${document?.filename.replace('.pdf', '')}_export.txt`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Plain text exported successfully')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to export text'
      
      if (retryCount < 2) {
        // Show retry option
        toast.error(
          <div>
            <p>{message}</p>
            <button 
              onClick={() => handleExportText(retryCount + 1)}
              className="mt-2 text-xs underline hover:text-accent-blue"
            >
              Retry
            </button>
          </div>,
          { duration: 5000 }
        )
      } else {
        toast.error(`${message} (after ${retryCount + 1} attempts)`)
      }
    } finally {
      setExportingText(false)
    }
  }

  if (isLoading || !document) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-green"></div>
      </div>
    )
  }

  const canShowExtracted = ['EXTRACTED', 'APPROVED', 'REJECTED', 'ESCALATED'].includes(document.status)
  const canApprove = document.status === 'EXTRACTED'
  const canParse = document.status === 'PENDING'

  return (
    <div className="h-full flex">
      {/* Document Sidebar */}
      <DocumentSidebar 
        isOpen={showSidebar} 
        onToggle={() => setShowSidebar(!showSidebar)} 
      />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
          >
            <ChevronLeft size={20} />
          </button>
          <div>
            <h1 className="text-xl font-bold">{document.filename}</h1>
            <p className="text-sm text-gray-400">
              Status: <span className="text-accent-green">{document.status}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {canShowExtracted && (
            <>
              <button
                onClick={() => setShowChat(!showChat)}
                className="btn btn-primary flex items-center gap-2"
              >
                <MessageSquare size={16} />
                {showChat ? 'Close Chat' : 'Open Chat'}
              </button>
              <button
                onClick={() => handleExportCsv()}
                disabled={exportingCsv || exportingMarkdown || exportingText}
                className="btn btn-secondary flex items-center gap-2"
              >
                {exportingCsv ? (
                  <>
                    <Loader className="animate-spin" size={16} />
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download size={16} />
                    Export CSV
                  </>
                )}
              </button>
              <button
                onClick={() => handleExportText()}
                disabled={exportingCsv || exportingMarkdown || exportingText}
                className="btn btn-secondary flex items-center gap-2"
              >
                {exportingText ? (
                  <>
                    <Loader className="animate-spin" size={16} />
                    Exporting...
                  </>
                ) : (
                  <>
                    <FileText size={16} />
                    Export Text
                  </>
                )}
              </button>
              <button
                onClick={() => handleExportMarkdown()}
                disabled={exportingCsv || exportingMarkdown || exportingText}
                className="btn btn-secondary flex items-center gap-2"
              >
                {exportingMarkdown ? (
                  <>
                    <Loader className="animate-spin" size={16} />
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download size={16} />
                    Export Markdown
                  </>
                )}
              </button>
            </>
          )}
          
          {canParse && (
            <button
              onClick={() => parseMutation.mutate()}
              disabled={parseMutation.isLoading}
              className="btn btn-primary"
            >
              {parseMutation.isLoading ? (
                <>
                  <Loader className="animate-spin mr-2" size={16} />
                  Parsing...
                </>
              ) : (
                'Start Extraction'
              )}
            </button>
          )}

          {canApprove && (
            <>
              <button
                onClick={() => approveMutation.mutate()}
                disabled={approveMutation.isLoading}
                className="btn btn-primary flex items-center gap-2"
              >
                <CheckCircle size={16} />
                Approve
              </button>
              <button
                onClick={() => rejectMutation.mutate(undefined)}
                disabled={rejectMutation.isLoading}
                className="btn btn-danger flex items-center gap-2"
              >
                <XCircle size={16} />
                Reject
              </button>
              <button
                onClick={() => escalateMutation.mutate(undefined)}
                disabled={escalateMutation.isLoading}
                className="btn btn-secondary flex items-center gap-2"
              >
                <AlertTriangle size={16} />
                Escalate
              </button>
            </>
          )}

        </div>
      </div>

      {/* Dual Pane View */}
      <div className="flex-1 grid grid-cols-2 gap-4 min-h-0">
        {/* PDF Viewer */}
        <div className="card p-4 flex flex-col">
          <h2 className="font-medium mb-2">Original PDF</h2>
          <PDFViewer 
            url={getDocumentPdf(documentId)}
            highlightAreas={highlightAreas}
            onHighlightsClear={() => setHighlightAreas([])}
          />
        </div>

        {/* Extracted Content */}
        <div className="card p-4 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-medium">Extracted Content</h2>
          </div>
          
          <div className="flex-1 overflow-auto">
            {document.status === 'PENDING' && (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <FileText size={48} className="mb-4" />
                <p>Click "Start Extraction" to begin processing</p>
              </div>
            )}
            
            {['parsing', 'extracting'].includes(document.status) && (
              <div className="flex flex-col items-center justify-center h-full">
                <Loader className="animate-spin mb-4" size={48} />
                <p className="text-gray-400">Processing document...</p>
              </div>
            )}
            
            {canShowExtracted && document.extracted_data && (
              <div className="mb-6">
                <div className="bg-dark-700 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-300 mb-3">Extracted Fields</h3>
                  <div className="space-y-2">
                    {Object.entries(typeof document.extracted_data === 'string' ? 
                      JSON.parse(document.extracted_data) : document.extracted_data)
                      .filter(([key]) => key !== 'chunks' && key !== 'full_content')
                      .map(([key, value]) => (
                        <div key={key} className="flex">
                          <span className="text-gray-400 min-w-[150px]">{key.replace(/_/g, ' ')}:</span>
                          <span className="text-white">
                            {Array.isArray(value) ? (
                              value.length > 0 ? (
                                <div className="space-y-1">
                                  {value.map((item, index) => (
                                    <div key={index} className="pl-2">
                                      • {String(item)}
                                    </div>
                                  ))}
                                </div>
                              ) : '(empty)'
                            ) : String(value || '(empty)')}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            )}

            {canShowExtracted && (markdownData || document.extracted_md) && 
             (!document.extracted_data || Object.keys(typeof document.extracted_data === 'string' ? 
              JSON.parse(document.extracted_data || '{}') : (document.extracted_data || {})).length === 0 || 
              Object.keys(typeof document.extracted_data === 'string' ? 
               JSON.parse(document.extracted_data || '{}') : (document.extracted_data || {})).every(k => k === 'full_content' || k === 'chunks')) && (
              <div className="prose prose-invert max-w-none prose-table:border-collapse prose-td:border prose-td:border-gray-600 prose-th:border prose-th:border-gray-600 prose-th:bg-dark-700 prose-td:p-2 prose-th:p-2">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    table: ({children}) => (
                      <table className="w-full border-collapse border border-gray-600">
                        {children}
                      </table>
                    ),
                    thead: ({children}) => (
                      <thead className="bg-dark-700">
                        {children}
                      </thead>
                    ),
                    tbody: ({children}) => (
                      <tbody>
                        {children}
                      </tbody>
                    ),
                    tr: ({children}) => (
                      <tr className="border-b border-gray-600">
                        {children}
                      </tr>
                    ),
                    th: ({children}) => (
                      <th className="border border-gray-600 p-2 text-left font-semibold">
                        {children}
                      </th>
                    ),
                    td: ({children}) => (
                      <td className="border border-gray-600 p-2">
                        {children}
                      </td>
                    ),
                    p: ({children}) => (
                      <p className="mb-4">
                        {children}
                      </p>
                    ),
                    h1: ({children}) => (
                      <h1 className="text-2xl font-bold mb-4 text-white">
                        {children}
                      </h1>
                    ),
                    h2: ({children}) => (
                      <h2 className="text-xl font-semibold mb-3 text-white">
                        {children}
                      </h2>
                    ),
                    h3: ({children}) => (
                      <h3 className="text-lg font-semibold mb-2 text-white">
                        {children}
                      </h3>
                    ),
                    ul: ({children}) => (
                      <ul className="list-disc list-inside mb-4">
                        {children}
                      </ul>
                    ),
                    ol: ({children}) => (
                      <ol className="list-decimal list-inside mb-4">
                        {children}
                      </ol>
                    ),
                    li: ({children}) => (
                      <li className="mb-1">
                        {children}
                      </li>
                    ),
                    code: ({children}) => {
                      const isInline = !String(children).includes('\n')
                      return isInline ? (
                        <code className="bg-dark-700 px-1 py-0.5 rounded text-accent-green">
                          {children}
                        </code>
                      ) : (
                        <code className="block bg-dark-700 p-3 rounded mb-4 overflow-x-auto">
                          {children}
                        </code>
                      )
                    },
                    blockquote: ({children}) => (
                      <blockquote className="border-l-4 border-accent-green pl-4 mb-4 italic">
                        {children}
                      </blockquote>
                    ),
                    hr: () => (
                      <hr className="border-gray-600 my-6" />
                    )
                  }}
                >
                  {markdownData?.markdown || document.extracted_md || ''}
                </ReactMarkdown>
              </div>
            )}
            
            {document.status === 'FAILED' && (
              <div className="flex items-center justify-center h-full p-8">
                <div className="max-w-md w-full">
                  <ErrorDisplay
                    error={{
                      message: document.error_message || 'Extraction failed',
                      code: document.error_message?.includes('Landing AI') ? 'LANDING_AI_ERROR' : 
                            document.error_message?.includes('validation') ? 'SCHEMA_VALIDATION_ERROR' :
                            'EXTRACTION_ERROR'
                    }}
                    retryAllowed={true}
                    escalationAvailable={true}
                    onRetry={() => retryMutation.mutate()}
                    onEscalate={() => escalateMutation.mutate(undefined)}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chat Sidebar */}
      {showChat && (
        <Chat
          documentId={documentId}
          documentStatus={document.status}
          onClose={() => setShowChat(false)}
          onHighlight={(areas) => setHighlightAreas(areas)}
        />
      )}

      {/* Field Selector Modal */}
      {showFieldSelector && parseMutation.data && (
        <FieldSelector
          fields={parseMutation.data.fields}
          onSelect={(fields, customFields) => extractMutation.mutate({ selectedFields: fields, customFields })}
          onClose={() => setShowFieldSelector(false)}
          isLoading={extractMutation.isLoading}
        />
      )}
      </div>
    </div>
  )
}