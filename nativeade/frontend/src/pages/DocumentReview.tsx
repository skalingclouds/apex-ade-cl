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
  getDocumentMarkdown
} from '../services/api'
import Chat from '../components/Chat'
import FieldSelector from '../components/FieldSelector'

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
  })

  const extractMutation = useMutation(
    (selectedFields: string[]) => extractDocument(documentId, selectedFields),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['document', documentId])
        setShowFieldSelector(false)
        toast.success('Document extracted successfully')
      },
    }
  )

  const handleExportCsv = async () => {
    try {
      const blob = await exportDocumentCsv(documentId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${document?.filename.replace('.pdf', '')}_export.csv`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('CSV exported successfully')
    } catch (error) {
      toast.error('Failed to export CSV')
    }
  }

  const handleExportMarkdown = async () => {
    try {
      const blob = await exportDocumentMarkdown(documentId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${document?.filename.replace('.pdf', '')}_export.md`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Markdown exported successfully')
    } catch (error) {
      toast.error('Failed to export Markdown')
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
    <div className="h-full flex flex-col">
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
                onClick={handleExportCsv}
                className="btn btn-secondary flex items-center gap-2"
              >
                <Download size={16} />
                Export CSV
              </button>
              <button
                onClick={handleExportMarkdown}
                className="btn btn-secondary flex items-center gap-2"
              >
                <Download size={16} />
                Export Markdown
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
            <h2 className="font-medium">Original PDF</h2>
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
            </div>
          </div>
          
          <div className="flex-1 overflow-auto">
            <PDFDocument
              file={getDocumentPdf(documentId)}
              onLoadSuccess={({ numPages }) => setNumPages(numPages)}
              className="pdf-document"
            >
              <PDFDocument.Page 
                pageNumber={pageNumber}
                className="pdf-page"
                width={500}
              />
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
              <div className="flex flex-col items-center justify-center h-full">
                <XCircle className="text-accent-red mb-4" size={48} />
                <p className="text-accent-red">Extraction failed</p>
                {document.error_message && (
                  <p className="text-sm text-gray-400 mt-2">{document.error_message}</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chat Sidebar */}
      {showChat && (
        <Chat
          documentId={documentId}
          onClose={() => setShowChat(false)}
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
  )
}