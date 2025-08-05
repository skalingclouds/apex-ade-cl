import { Link } from 'react-router-dom'
import { FileText, Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import { Document } from '../services/api'
import { formatDistanceToNow } from '../utils/date'

interface DocumentCardProps {
  document: Document
}

export default function DocumentCard({ document }: DocumentCardProps) {
  const statusConfig = {
    pending: { icon: Clock, color: 'text-gray-400', bg: 'bg-gray-400/10' },
    parsing: { icon: Clock, color: 'text-accent-yellow', bg: 'bg-accent-yellow/10' },
    parsed: { icon: Clock, color: 'text-accent-yellow', bg: 'bg-accent-yellow/10' },
    extracting: { icon: Clock, color: 'text-accent-yellow', bg: 'bg-accent-yellow/10' },
    extracted: { icon: CheckCircle, color: 'text-accent-green', bg: 'bg-accent-green/10' },
    approved: { icon: CheckCircle, color: 'text-accent-green', bg: 'bg-accent-green/10' },
    rejected: { icon: XCircle, color: 'text-accent-red', bg: 'bg-accent-red/10' },
    escalated: { icon: AlertTriangle, color: 'text-accent-yellow', bg: 'bg-accent-yellow/10' },
    failed: { icon: XCircle, color: 'text-accent-red', bg: 'bg-accent-red/10' },
  }

  const config = statusConfig[document.status]
  const StatusIcon = config.icon

  return (
    <Link
      to={`/documents/${document.id}`}
      className="block p-4 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${config.bg}`}>
            <StatusIcon className={config.color} size={20} />
          </div>
          <div>
            <h4 className="font-medium">{document.filename}</h4>
            <p className="text-sm text-gray-400">
              Uploaded {formatDistanceToNow(document.uploaded_at)}
            </p>
          </div>
        </div>
        <div className="text-right">
          <span className={`text-sm font-medium ${config.color}`}>
            {document.status.charAt(0).toUpperCase() + document.status.slice(1)}
          </span>
          {document.processed_at && (
            <p className="text-xs text-gray-500 mt-1">
              Processed {formatDistanceToNow(document.processed_at)}
            </p>
          )}
        </div>
      </div>
    </Link>
  )
}