import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation } from 'react-query'
import { Send, X, Loader } from 'lucide-react'
import { chatWithDocument, getChatHistory, ChatResponse } from '../services/api'

interface ChatProps {
  documentId: number
  onClose: () => void
}

export default function Chat({ documentId, onClose }: ChatProps) {
  const [message, setMessage] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const { data: history, refetch } = useQuery(
    ['chat-history', documentId],
    () => getChatHistory(documentId)
  )

  const sendMessageMutation = useMutation(
    (query: string) => chatWithDocument(documentId, query),
    {
      onSuccess: () => {
        setMessage('')
        refetch()
      },
    }
  )

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [history])

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim()) {
      sendMessageMutation.mutate(message.trim())
    }
  }

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-dark-800 border-l border-dark-600 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-dark-600">
        <h3 className="font-medium">Chat with Document</h3>
        <button
          onClick={onClose}
          className="p-1 hover:bg-dark-700 rounded transition-colors"
        >
          <X size={20} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {history?.map((msg) => (
          <div key={msg.id} className="space-y-2">
            <div className="flex justify-end">
              <div className="bg-accent-green/20 text-white px-4 py-2 rounded-lg max-w-[80%]">
                {msg.query}
              </div>
            </div>
            <div className="flex justify-start">
              <div className="bg-dark-700 px-4 py-2 rounded-lg max-w-[80%]">
                {msg.response}
                {msg.highlighted_areas && msg.highlighted_areas.length > 0 && (
                  <p className="text-xs text-gray-400 mt-2">
                    📍 {msg.highlighted_areas.length} areas highlighted in PDF
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {sendMessageMutation.isLoading && (
          <div className="flex justify-start">
            <div className="bg-dark-700 px-4 py-2 rounded-lg">
              <Loader className="animate-spin" size={16} />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="p-4 border-t border-dark-600">
        <div className="flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask a question about the document..."
            className="input flex-1"
            disabled={sendMessageMutation.isLoading}
          />
          <button
            type="submit"
            disabled={!message.trim() || sendMessageMutation.isLoading}
            className="btn btn-primary p-2"
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  )
}