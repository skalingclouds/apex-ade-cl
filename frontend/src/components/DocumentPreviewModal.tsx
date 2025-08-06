import { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { X, FileText, FileSpreadsheet, FileCode, Copy, Check } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import toast from 'react-hot-toast'
import PDFViewer from './PDFViewer'
import { 
  getDocument, 
  getDocumentPdf, 
  getDocumentMarkdown,
  exportDocumentCsv,
  exportDocumentMarkdown,
  exportDocumentText
} from '../services/api'

interface DocumentPreviewModalProps {
  documentId: number
  onClose: () => void
}

export default function DocumentPreviewModal({ documentId, onClose }: DocumentPreviewModalProps) {
  const [activeView, setActiveView] = useState<'split' | 'pdf' | 'markdown'>('split')
  const [copiedToClipboard, setCopiedToClipboard] = useState(false)

  // Fetch document details
  const { data: document, isLoading: docLoading } = useQuery(
    ['document', documentId],
    () => getDocument(documentId) as any,
    {
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to load document')
      }
    }
  )

  // Fetch markdown content
  const { data: markdownData, isLoading: mdLoading } = useQuery(
    ['document-markdown', documentId],
    () => getDocumentMarkdown(documentId),
    {
      enabled: !!document && (document as any).status === 'EXTRACTED',
      onError: (error: any) => {
        console.error('Failed to load markdown:', error)
      }
    }
  )

  // Handle export actions
  const handleExport = async (format: 'csv' | 'markdown' | 'text') => {
    try {
      let blob: Blob
      let filename: string
      
      switch (format) {
        case 'csv':
          blob = await exportDocumentCsv(documentId)
          filename = `${(document as any)?.filename.replace('.pdf', '')}_export.csv`
          break
        case 'markdown':
          blob = await exportDocumentMarkdown(documentId)
          filename = `${(document as any)?.filename.replace('.pdf', '')}_export.md`
          break
        case 'text':
          blob = await exportDocumentText(documentId)
          filename = `${(document as any)?.filename.replace('.pdf', '')}_export.txt`
          break
      }

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = window.document.createElement('a')
      a.href = url
      a.download = filename
      window.document.body.appendChild(a)
      a.click()
      window.document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      toast.success(`Exported as ${format.toUpperCase()}`)
    } catch (error: any) {
      toast.error(`Failed to export as ${format}`)
      console.error('Export error:', error)
    }
  }

  // Handle copy to clipboard
  const handleCopyMarkdown = async () => {
    if (markdownData?.markdown) {
      try {
        await navigator.clipboard.writeText(markdownData.markdown)
        setCopiedToClipboard(true)
        toast.success('Copied to clipboard')
        setTimeout(() => setCopiedToClipboard(false), 2000)
      } catch (error) {
        toast.error('Failed to copy to clipboard')
      }
    }
  }

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  const isLoading = docLoading || mdLoading
  const pdfUrl = getDocumentPdf(documentId)

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-dark-800 rounded-lg max-w-7xl w-full h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700">
          <div className="flex items-center gap-4">
            <FileText size={24} className="text-accent-blue" />
            <div>
              <h2 className="text-xl font-semibold">{(document as any)?.filename || 'Loading...'}</h2>
              {document && (
                <p className="text-sm text-gray-400 mt-1">
                  Status: <span className={`capitalize ${
                    (document as any).status === 'APPROVED' ? 'text-green-400' :
                    (document as any).status === 'REJECTED' ? 'text-red-400' :
                    (document as any).status === 'ESCALATED' ? 'text-yellow-400' :
                    'text-gray-400'
                  }`}>{(document as any).status.toLowerCase()}</span>
                  {(document as any).processed_at && ` • Processed: ${new Date((document as any).processed_at).toLocaleDateString()}`}
                </p>
              )}
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 hover:bg-dark-700 rounded transition-colors"
            title="Close (Esc)"
          >
            <X size={20} />
          </button>
        </div>

        {/* View Toggle */}
        <div className="flex items-center justify-between px-6 py-3 border-b border-gray-700">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveView('split')}
              className={`px-4 py-2 rounded transition-colors ${
                activeView === 'split' 
                  ? 'bg-accent-blue text-white' 
                  : 'bg-dark-700 hover:bg-dark-600'
              }`}
            >
              Split View
            </button>
            <button
              onClick={() => setActiveView('pdf')}
              className={`px-4 py-2 rounded transition-colors ${
                activeView === 'pdf' 
                  ? 'bg-accent-blue text-white' 
                  : 'bg-dark-700 hover:bg-dark-600'
              }`}
            >
              PDF Only
            </button>
            <button
              onClick={() => setActiveView('markdown')}
              className={`px-4 py-2 rounded transition-colors ${
                activeView === 'markdown' 
                  ? 'bg-accent-blue text-white' 
                  : 'bg-dark-700 hover:bg-dark-600'
              }`}
              disabled={!markdownData?.markdown}
            >
              Extracted Text Only
            </button>
          </div>

          {/* Export Buttons */}
          <div className="flex items-center gap-2">
            {markdownData?.markdown && (
              <button
                onClick={handleCopyMarkdown}
                className="px-3 py-2 bg-dark-700 hover:bg-dark-600 rounded transition-colors flex items-center gap-2"
                title="Copy markdown to clipboard"
              >
                {copiedToClipboard ? <Check size={16} /> : <Copy size={16} />}
                Copy
              </button>
            )}
            
            <button
              onClick={() => handleExport('csv')}
              className="px-3 py-2 bg-dark-700 hover:bg-dark-600 rounded transition-colors flex items-center gap-2"
              disabled={!document || (document as any).status !== 'EXTRACTED'}
              title="Export as CSV"
            >
              <FileSpreadsheet size={16} />
              CSV
            </button>
            
            <button
              onClick={() => handleExport('markdown')}
              className="px-3 py-2 bg-dark-700 hover:bg-dark-600 rounded transition-colors flex items-center gap-2"
              disabled={!document || (document as any).status !== 'EXTRACTED'}
              title="Export as Markdown"
            >
              <FileCode size={16} />
              Markdown
            </button>
            
            <button
              onClick={() => handleExport('text')}
              className="px-3 py-2 bg-dark-700 hover:bg-dark-600 rounded transition-colors flex items-center gap-2"
              disabled={!document || (document as any).status !== 'EXTRACTED'}
              title="Export as Plain Text"
            >
              <FileText size={16} />
              Text
            </button>
          </div>
        </div>

        {/* Content Area */}
        {isLoading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-blue"></div>
          </div>
        ) : (
          <div className="flex-1 overflow-hidden flex">
            {/* PDF Viewer */}
            {(activeView === 'split' || activeView === 'pdf') && (
              <div className={`${activeView === 'split' ? 'w-1/2' : 'w-full'} h-full p-4`}>
                <div className="h-full rounded-lg overflow-hidden">
                  <PDFViewer url={pdfUrl} />
                </div>
              </div>
            )}
            
            {/* Divider for split view */}
            {activeView === 'split' && (
              <div className="w-px bg-gray-700" />
            )}
            
            {/* Markdown Viewer */}
            {(activeView === 'split' || activeView === 'markdown') && (
              <div className={`${activeView === 'split' ? 'w-1/2' : 'w-full'} h-full p-4`}>
                <div className="h-full bg-dark-700 rounded-lg overflow-hidden">
                  <div className="h-full flex flex-col">
                    <div className="px-4 py-3 border-b border-gray-600">
                      <h3 className="font-medium">Extracted Content</h3>
                      {markdownData?.processed_at && (
                        <p className="text-xs text-gray-400 mt-1">
                          Processed: {new Date(markdownData.processed_at).toLocaleString()}
                        </p>
                      )}
                    </div>
                    
                    <div className="flex-1 overflow-auto p-4">
                      {markdownData?.markdown || (document as any)?.extracted_md ? (
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
                                  <code className="block bg-dark-800 p-3 rounded mb-4 overflow-x-auto">
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
                            {markdownData?.markdown || (document as any)?.extracted_md || ''}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <div className="text-center text-gray-500 mt-8">
                          <FileText size={48} className="mx-auto mb-4 opacity-50" />
                          <p>No extracted content available</p>
                          {(document as any)?.status === 'PENDING' && (
                            <p className="text-sm mt-2">Document is pending extraction</p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}