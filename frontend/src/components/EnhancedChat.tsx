import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation } from 'react-query'
import { 
  Send, 
  X, 
  Loader, 
  MessageSquare, 
  Highlighter,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  User,
  Bot,
  Clock,
  AlertCircle
} from 'lucide-react'
import toast from 'react-hot-toast'
import PDFViewer from './PDFViewer'
import { chatWithDocument, getChatHistory, getDocumentPdf, ChatResponse } from '../services/api'
import { Document } from '../types/document'

interface EnhancedChatProps {
  document: Document
  onClose: () => void
}

// Remove unused Message interface since we use ChatResponse

export default function EnhancedChat({ document, onClose }: EnhancedChatProps) {
  const [message, setMessage] = useState('')
  const [activeHighlights, setActiveHighlights] = useState<Array<{ page: number; bbox: number[] }>>([])
  const [expandedMessages, setExpandedMessages] = useState<Set<number>>(new Set())
  const [copiedMessageId, setCopiedMessageId] = useState<number | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  
  // Fetch chat history
  const { data: history, isLoading: historyLoading, refetch } = useQuery<ChatResponse[]>(
    ['chat-history', document.id],
    () => getChatHistory(document.id),
    {
      onError: () => {
        toast.error('Failed to load chat history')
      }
    }
  )

  // Send message mutation
  const sendMessageMutation = useMutation(
    (query: string) => chatWithDocument(document.id, query),
    {
      onSuccess: (response) => {
        setMessage('')
        refetch()
        
        // Highlight areas in PDF if available
        if (response.highlighted_areas && response.highlighted_areas.length > 0) {
          // Pass through the areas directly - they already have the correct format
          setActiveHighlights(response.highlighted_areas)
          toast.success(`Found ${response.highlighted_areas.length} relevant sections`)
        }
        
        // Auto-expand the latest message
        if (response.id) {
          setExpandedMessages(prev => new Set([...prev, response.id]))
        }
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to send message')
      }
    }
  )

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [history])

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  // Handle send message
  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !sendMessageMutation.isLoading) {
      sendMessageMutation.mutate(message.trim())
    }
  }

  // Toggle message expansion
  const toggleMessageExpansion = (messageId: number) => {
    setExpandedMessages(prev => {
      const newSet = new Set(prev)
      if (newSet.has(messageId)) {
        newSet.delete(messageId)
      } else {
        newSet.add(messageId)
      }
      return newSet
    })
  }

  // Copy response to clipboard
  const copyToClipboard = async (text: string, messageId: number) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedMessageId(messageId)
      toast.success('Copied to clipboard')
      setTimeout(() => setCopiedMessageId(null), 2000)
    } catch (error) {
      toast.error('Failed to copy to clipboard')
    }
  }

  // Clear highlights
  const clearHighlights = () => {
    setActiveHighlights([])
  }

  // Show highlights from a specific message
  const showMessageHighlights = (highlights: any[]) => {
    // Highlights already have the correct format with page and bbox
    setActiveHighlights(highlights)
    toast.success(`Showing ${highlights.length} highlighted areas`)
  }

  const pdfUrl = getDocumentPdf(document.id)

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-dark-800 rounded-lg max-w-7xl w-full h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700">
          <div className="flex items-center gap-4">
            <MessageSquare size={24} className="text-accent-blue" />
            <div>
              <h2 className="text-xl font-semibold">Chat with Document</h2>
              <p className="text-sm text-gray-400">{document.filename}</p>
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

        {/* Main Content - Split View */}
        <div className="flex-1 flex overflow-hidden">
          {/* PDF Viewer - Left Side */}
          <div className="w-1/2 border-r border-gray-700 p-4">
            <div className="h-full">
              <PDFViewer 
                url={pdfUrl} 
                highlightAreas={activeHighlights}
                onHighlightsClear={clearHighlights}
              />
            </div>
          </div>

          {/* Chat Interface - Right Side */}
          <div className="w-1/2 flex flex-col">
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {historyLoading ? (
                <div className="flex items-center justify-center h-full">
                  <Loader className="animate-spin" size={32} />
                </div>
              ) : history && history.length > 0 ? (
                history.map((msg) => {
                  const isExpanded = expandedMessages.has(msg.id)
                  const truncatedResponse = msg.response.length > 200 && !isExpanded
                    ? msg.response.substring(0, 200) + '...'
                    : msg.response

                  return (
                    <div key={msg.id} className="space-y-3">
                      {/* User Query */}
                      <div className="flex gap-3">
                        <div className="flex-shrink-0 w-8 h-8 bg-accent-green/20 rounded-full flex items-center justify-center">
                          <User size={16} className="text-accent-green" />
                        </div>
                        <div className="flex-1">
                          <div className="bg-accent-green/10 border border-accent-green/20 text-white px-4 py-3 rounded-lg">
                            {msg.query}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            <Clock size={10} className="inline mr-1" />
                            {new Date(msg.created_at).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>

                      {/* AI Response */}
                      <div className="flex gap-3">
                        <div className="flex-shrink-0 w-8 h-8 bg-accent-blue/20 rounded-full flex items-center justify-center">
                          <Bot size={16} className="text-accent-blue" />
                        </div>
                        <div className="flex-1">
                          <div className="bg-dark-700 px-4 py-3 rounded-lg">
                            <div className="text-sm leading-relaxed">
                              {truncatedResponse}
                            </div>
                            
                            {/* Action Buttons */}
                            <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-600">
                              {msg.response.length > 200 && (
                                <button
                                  onClick={() => toggleMessageExpansion(msg.id)}
                                  className="text-xs text-gray-400 hover:text-white flex items-center gap-1"
                                >
                                  {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                                  {isExpanded ? 'Show less' : 'Show more'}
                                </button>
                              )}
                              
                              {msg.highlighted_areas && msg.highlighted_areas.length > 0 && (
                                <button
                                  onClick={() => showMessageHighlights(msg.highlighted_areas!)}
                                  className="text-xs text-accent-blue hover:text-accent-blue/80 flex items-center gap-1"
                                >
                                  <Highlighter size={14} />
                                  Show {msg.highlighted_areas.length} highlights
                                </button>
                              )}
                              
                              <button
                                onClick={() => copyToClipboard(msg.response, msg.id)}
                                className="text-xs text-gray-400 hover:text-white flex items-center gap-1 ml-auto"
                              >
                                {copiedMessageId === msg.id ? (
                                  <>
                                    <Check size={14} />
                                    Copied
                                  </>
                                ) : (
                                  <>
                                    <Copy size={14} />
                                    Copy
                                  </>
                                )}
                              </button>
                            </div>

                            {/* Metadata */}
                            {(msg as any).fallback && (
                              <div className="flex items-center gap-2 mt-2 text-xs text-yellow-500">
                                <AlertCircle size={12} />
                                Using fallback model
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <MessageSquare size={48} className="mb-4 opacity-50" />
                  <p>No messages yet</p>
                  <p className="text-sm mt-2">Ask a question about the document to get started</p>
                </div>
              )}
              
              {/* Loading indicator for sending message */}
              {sendMessageMutation.isLoading && (
                <div className="flex gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-accent-blue/20 rounded-full flex items-center justify-center">
                    <Bot size={16} className="text-accent-blue animate-pulse" />
                  </div>
                  <div className="flex-1">
                    <div className="bg-dark-700 px-4 py-3 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Loader className="animate-spin" size={16} />
                        <span className="text-sm text-gray-400">Thinking...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-700 p-4">
              {document.status === 'REJECTED' ? (
                <div className="text-center text-gray-400 py-2">
                  <AlertCircle size={20} className="inline mb-1" />
                  <p className="text-sm">Chat is disabled for rejected documents</p>
                </div>
              ) : document.status !== 'EXTRACTED' && document.status !== 'APPROVED' ? (
                <div className="text-center text-gray-400 py-2">
                  <AlertCircle size={20} className="inline mb-1" />
                  <p className="text-sm">Document must be extracted before chat is available</p>
                </div>
              ) : (
                <form onSubmit={handleSend} className="flex gap-2">
                  <input
                    ref={inputRef}
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Ask a question about the document..."
                    className="flex-1 px-4 py-2 bg-dark-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-blue"
                    disabled={sendMessageMutation.isLoading}
                  />
                  <button
                    type="submit"
                    disabled={!message.trim() || sendMessageMutation.isLoading}
                    className="px-4 py-2 bg-accent-blue hover:bg-accent-blue/80 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center gap-2"
                  >
                    {sendMessageMutation.isLoading ? (
                      <Loader className="animate-spin" size={20} />
                    ) : (
                      <Send size={20} />
                    )}
                    Send
                  </button>
                </form>
              )}

              {/* Highlight Status */}
              {activeHighlights.length > 0 && (
                <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
                  <span className="flex items-center gap-1">
                    <Highlighter size={12} />
                    {activeHighlights.length} areas highlighted
                  </span>
                  <button
                    onClick={clearHighlights}
                    className="hover:text-white transition-colors"
                  >
                    Clear highlights
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}