import { AlertTriangle, RefreshCw, HelpCircle } from 'lucide-react'
import { useState } from 'react'

interface ErrorInfo {
  message: string
  code?: string
  type?: string
}

interface ErrorDisplayProps {
  error: ErrorInfo
  retryAllowed?: boolean
  escalationAvailable?: boolean
  onRetry?: () => void
  onEscalate?: () => void
}

export default function ErrorDisplay({ 
  error, 
  retryAllowed = false, 
  escalationAvailable = false,
  onRetry,
  onEscalate 
}: ErrorDisplayProps) {
  const [showDetails, setShowDetails] = useState(false)
  
  const getErrorSeverity = (code?: string) => {
    if (!code) return 'error'
    
    if (code.includes('VALIDATION')) return 'warning'
    if (code.includes('NOT_FOUND')) return 'error'
    if (code.includes('LANDING_AI')) return 'critical'
    
    return 'error'
  }
  
  const severity = getErrorSeverity(error.code)
  
  const severityStyles = {
    warning: 'bg-yellow-900/20 border-yellow-700 text-yellow-400',
    error: 'bg-red-900/20 border-red-700 text-red-400',
    critical: 'bg-purple-900/20 border-purple-700 text-purple-400'
  }
  
  return (
    <div className={`rounded-lg border p-4 ${severityStyles[severity]}`}>
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5" size={20} />
        <div className="flex-1">
          <h3 className="font-medium mb-1">
            {error.code === 'SCHEMA_VALIDATION_ERROR' && 'Validation Error'}
            {error.code === 'LANDING_AI_ERROR' && 'Service Unavailable'}
            {error.code === 'EXTRACTION_ERROR' && 'Extraction Failed'}
            {!error.code && 'Error'}
          </h3>
          
          <p className="text-sm opacity-90 mb-3">{error.message}</p>
          
          {error.code && (
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-xs opacity-70 hover:opacity-100 transition-opacity flex items-center gap-1"
            >
              <HelpCircle size={14} />
              {showDetails ? 'Hide' : 'Show'} error details
            </button>
          )}
          
          {showDetails && (
            <div className="mt-2 p-2 bg-black/20 rounded text-xs font-mono">
              <div>Code: {error.code}</div>
              {error.type && <div>Type: {error.type}</div>}
            </div>
          )}
          
          <div className="flex gap-2 mt-4">
            {retryAllowed && onRetry && (
              <button
                onClick={onRetry}
                className="btn btn-sm btn-secondary flex items-center gap-2"
              >
                <RefreshCw size={14} />
                Retry
              </button>
            )}
            
            {escalationAvailable && onEscalate && (
              <button
                onClick={onEscalate}
                className="btn btn-sm btn-secondary flex items-center gap-2"
              >
                <AlertTriangle size={14} />
                Escalate
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}