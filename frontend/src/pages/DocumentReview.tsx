import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { Document as PDFDocument } from 'react-pdf'
import { pdfjs } from 'react-pdf'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'
import ReactMarkdown from 'react-markdown'
import toast from 'react-hot-toast'
import { 
  ChevronLeft, 
  ChevronRight, 
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
  getDocumentMarkdown,
  retryExtraction
} from '../services/api'
import Chat from '../components/Chat'
import FieldSelector from '../components/FieldSelector'
import ErrorDisplay from '../components/ErrorDisplay'
import DocumentSidebar from '../components/DocumentSidebar'

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`

export default function DocumentReview() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const [numPages, setNumPages] = useState<number>(0)
  const [pageNumber, setPageNumber] = useState<number>(1)
  const [showChat, setShowChat] = useState(false)
  const [showFieldSelector, setShowFieldSelector] = useState(false)
  const [showSidebar, setShowSidebar] = useState(true)
  const [highlightAreas, setHighlightAreas] = useState<Array<{ page: number; bbox: number[] }>>([])
  const [exportingCsv, setExportingCsv] = useState(false)
  const [exportingMarkdown, setExportingMarkdown] = useState(false)
  
  const documentId = parseInt(id!)

  const { data: document, isLoading } = useQuery(
    ['document', documentId],
    () => getDocument(documentId),
    {
      refetchInterval: (data) => {
        // Poll while processing
        if (data && ['parsing', 'extracting'].includes(data.status)) {
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
      enabled: !!document && ['extracted', 'approved'].includes(document.status),
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
    onSuccess: (data) => {
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
    (selectedFields: string[]) => extractDocument(documentId, selectedFields),
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
      const a = document.createElement('a')
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
      const a = document.createElement('a')
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

  if (isLoading || !document) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-green"></div>
      </div>
    )
  }

  const canShowExtracted = ['extracted', 'approved', 'rejected', 'escalated'].includes(document.status)
  const canApprove = document.status === 'extracted'
  const canParse = document.status === 'pending'

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
                onClick={() => handleExportCsv()}
                disabled={exportingCsv || exportingMarkdown}
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
                onClick={() => handleExportMarkdown()}
                disabled={exportingCsv || exportingMarkdown}
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
                onClick={() => rejectMutation.mutate()}
                disabled={rejectMutation.isLoading}
                className="btn btn-danger flex items-center gap-2"
              >
                <XCircle size={16} />
                Reject
              </button>
              <button
                onClick={() => escalateMutation.mutate()}
                disabled={escalateMutation.isLoading}
                className="btn btn-secondary flex items-center gap-2"
              >
                <AlertTriangle size={16} />
                Escalate
              </button>
            </>
          )}

          {canShowExtracted && (
            <button
              onClick={() => setShowChat(!showChat)}
              className="btn btn-secondary flex items-center gap-2"
            >
              <MessageSquare size={16} />
              Chat
            </button>
          )}
        </div>
      </div>

      {/* Dual Pane View */}
      <div className="flex-1 grid grid-cols-2 gap-4 min-h-0">
        {/* PDF Viewer */}
        <div className="card p-4 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <h2 className="font-medium">Original PDF</h2>
              {highlightAreas.length > 0 && (
                <span className="text-xs bg-yellow-400/20 text-yellow-400 px-2 py-1 rounded">
                  {highlightAreas.filter(a => a.page === pageNumber).length} highlights on this page
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPageNumber(Math.max(1, pageNumber - 1))}
                disabled={pageNumber <= 1}
                className="p-1 hover:bg-dark-700 rounded disabled:opacity-50"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="text-sm">
                Page {pageNumber} of {numPages}
              </span>
              <button
                onClick={() => setPageNumber(Math.min(numPages, pageNumber + 1))}
                disabled={pageNumber >= numPages}
                className="p-1 hover:bg-dark-700 rounded disabled:opacity-50"
              >
                <ChevronRight size={16} />
              </button>
              {highlightAreas.length > 0 && (
                <button
                  onClick={() => setHighlightAreas([])}
                  className="ml-2 text-xs text-yellow-400 hover:text-yellow-300 transition-colors"
                >
                  Clear highlights
                </button>
              )}
            </div>
          </div>
          
          <div className="flex-1 overflow-auto relative">
            <PDFDocument
              file={getDocumentPdf(documentId)}
              onLoadSuccess={({ numPages }) => setNumPages(numPages)}
              className="pdf-document"
            >
              <div className="relative">
                <PDFDocument.Page 
                  pageNumber={pageNumber}
                  className="pdf-page"
                  width={500}
                />
                {/* Highlight Overlay */}
                {highlightAreas
                  .filter(area => area.page === pageNumber)
                  .map((area, index) => (
                    <div
                      key={index}
                      className="absolute bg-yellow-400 bg-opacity-30 pointer-events-none border-2 border-yellow-400"
                      style={{
                        left: `${(area.bbox[0] / 1000) * 100}%`,
                        top: `${(area.bbox[1] / 1000) * 100}%`,
                        width: `${((area.bbox[2] - area.bbox[0]) / 1000) * 100}%`,
                        height: `${((area.bbox[3] - area.bbox[1]) / 1000) * 100}%`,
                      }}
                    />
                  ))}
              </div>
            </PDFDocument>
          </div>
        </div>

        {/* Extracted Content */}
        <div className="card p-4 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-medium">Extracted Content</h2>
          </div>
          
          <div className="flex-1 overflow-auto">
            {document.status === 'pending' && (
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
            
            {canShowExtracted && markdownData && (
              <div className="prose prose-invert max-w-none">
                <ReactMarkdown>{markdownData.markdown}</ReactMarkdown>
              </div>
            )}
            
            {document.status === 'failed' && (
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
                    onEscalate={() => escalateMutation.mutate()}
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
          onSelect={(fields) => extractMutation.mutate(fields)}
          onClose={() => setShowFieldSelector(false)}
          isLoading={extractMutation.isLoading}
        />
      )}
      </div>
    </div>
  )
}