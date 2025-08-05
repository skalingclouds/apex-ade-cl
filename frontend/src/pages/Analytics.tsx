import { useQuery } from 'react-query'
import { 
  BarChart3, 
  FileText, 
  MessageSquare, 
  CheckCircle, 
  XCircle,
  TrendingUp,
  Download,
  Clock
} from 'lucide-react'

interface AnalyticsMetrics {
  total_documents: number
  status_distribution: Record<string, number>
  approval_rate: number
  rejection_rate: number
  total_chat_interactions: number
  unique_documents_chatted: number
  average_chats_per_document: number
  total_exports: number
  recent_uploads_24h: number
  recent_chats_24h: number
}

interface PerformanceMetrics {
  average_chat_response_time_ms: number
  document_failure_rate: number
  chat_fallback_rate: number
  total_failed_documents: number
  total_fallback_chats: number
}

export default function Analytics() {
  const { data: metrics, isLoading: metricsLoading } = useQuery<AnalyticsMetrics>(
    'analytics-metrics',
    async () => {
      const response = await fetch('/api/v1/analytics/metrics')
      if (!response.ok) throw new Error('Failed to fetch metrics')
      return response.json()
    },
    { refetchInterval: 30000 } // Refresh every 30 seconds
  )

  const { data: performance, isLoading: perfLoading } = useQuery<PerformanceMetrics>(
    'performance-metrics',
    async () => {
      const response = await fetch('/api/v1/analytics/metrics/performance')
      if (!response.ok) throw new Error('Failed to fetch performance metrics')
      return response.json()
    },
    { refetchInterval: 30000 }
  )

  if (metricsLoading || perfLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-blue mx-auto mb-4"></div>
          <p className="text-gray-500">Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (!metrics || !performance) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500">No analytics data available</p>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col gap-6 p-6">
      <div>
        <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
        <p className="text-gray-500 mt-1">Monitor system usage and performance metrics</p>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Documents</p>
              <p className="text-2xl font-bold">{metrics.total_documents}</p>
              <p className="text-xs text-gray-400 mt-1">
                {metrics.recent_uploads_24h} uploaded today
              </p>
            </div>
            <FileText className="text-accent-blue" size={32} />
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Approval Rate</p>
              <p className="text-2xl font-bold">{metrics.approval_rate}%</p>
              <div className="flex items-center gap-2 mt-1">
                <CheckCircle className="text-green-500" size={16} />
                <span className="text-xs text-gray-400">
                  {metrics.status_distribution.APPROVED || 0} approved
                </span>
              </div>
            </div>
            <TrendingUp className="text-green-500" size={32} />
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Chat Interactions</p>
              <p className="text-2xl font-bold">{metrics.total_chat_interactions}</p>
              <p className="text-xs text-gray-400 mt-1">
                {metrics.recent_chats_24h} today
              </p>
            </div>
            <MessageSquare className="text-accent-purple" size={32} />
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Exports</p>
              <p className="text-2xl font-bold">{metrics.total_exports}</p>
              <p className="text-xs text-gray-400 mt-1">
                CSV & Markdown
              </p>
            </div>
            <Download className="text-accent-green" size={32} />
          </div>
        </div>
      </div>

      {/* Status Distribution */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Document Status Distribution</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(metrics.status_distribution).map(([status, count]) => (
            <div key={status} className="text-center">
              <p className="text-sm text-gray-500 capitalize">{status.toLowerCase()}</p>
              <p className="text-xl font-bold">{count}</p>
              <div className="mt-2 h-2 bg-dark-700 rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all duration-500 ${
                    status === 'APPROVED' ? 'bg-green-500' :
                    status === 'REJECTED' ? 'bg-red-500' :
                    status === 'EXTRACTED' ? 'bg-blue-500' :
                    status === 'FAILED' ? 'bg-red-600' :
                    'bg-gray-500'
                  }`}
                  style={{ width: `${(count / metrics.total_documents) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4">Chat Performance</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock size={16} className="text-gray-500" />
                <span className="text-sm">Average Response Time</span>
              </div>
              <span className="font-semibold">
                {performance.average_chat_response_time_ms.toFixed(2)}ms
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare size={16} className="text-gray-500" />
                <span className="text-sm">Avg. Chats per Document</span>
              </div>
              <span className="font-semibold">
                {metrics.average_chats_per_document.toFixed(1)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <XCircle size={16} className="text-gray-500" />
                <span className="text-sm">Fallback Rate</span>
              </div>
              <span className="font-semibold">
                {performance.chat_fallback_rate.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4">System Health</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText size={16} className="text-gray-500" />
                <span className="text-sm">Document Failure Rate</span>
              </div>
              <span className={`font-semibold ${
                performance.document_failure_rate > 5 ? 'text-red-500' : 'text-green-500'
              }`}>
                {performance.document_failure_rate.toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle size={16} className="text-gray-500" />
                <span className="text-sm">Rejection Rate</span>
              </div>
              <span className="font-semibold">
                {metrics.rejection_rate.toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BarChart3 size={16} className="text-gray-500" />
                <span className="text-sm">Documents with Chat</span>
              </div>
              <span className="font-semibold">
                {metrics.unique_documents_chatted}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Admin Notice */}
      <div className="card p-4 bg-yellow-500/10 border-yellow-500/20">
        <div className="flex items-center gap-3">
          <div className="text-yellow-500">⚠️</div>
          <p className="text-sm">
            This dashboard contains sensitive analytics data and should be restricted to admin users only.
          </p>
        </div>
      </div>
    </div>
  )
}