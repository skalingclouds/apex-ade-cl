import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Document types
export interface Document {
  id: number
  filename: string
  filepath: string
  status: 'pending' | 'parsing' | 'parsed' | 'extracting' | 'extracted' | 'approved' | 'rejected' | 'escalated' | 'failed'
  extracted_md?: string
  extracted_data?: any
  error_message?: string
  uploaded_at: string
  processed_at?: string
  updated_at: string
}

export interface DocumentListResponse {
  documents: Document[]
  total: number
}

export interface DocumentStats {
  total: number
  pending: number
  completed: number
  failed: number
  completionRate: number
  successful: number
}

export interface ParseResponse {
  fields: FieldInfo[]
  document_type?: string
  confidence?: number
}

export interface FieldInfo {
  name: string
  type: string
  description?: string
  required: boolean
}

export interface ExtractionResponse {
  success: boolean
  extracted_data?: any
  markdown?: string
  error?: string
}

export interface ChatResponse {
  id: number
  query: string
  response: string
  highlighted_areas?: HighlightArea[]
  created_at: string
}

export interface HighlightArea {
  page: number
  x: number
  y: number
  width: number
  height: number
}

// API functions
export const uploadDocument = async (file: File): Promise<Document> => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const getDocuments = async (status?: string): Promise<DocumentListResponse> => {
  const params = status ? { status } : {}
  const response = await api.get('/documents', { params })
  return response.data
}

export const getDocument = async (id: number): Promise<Document> => {
  const response = await api.get(`/documents/${id}`)
  return response.data
}

export const deleteDocument = async (id: number): Promise<void> => {
  await api.delete(`/documents/${id}`)
}

export const parseDocument = async (id: number): Promise<ParseResponse> => {
  const response = await api.post(`/documents/${id}/parse`)
  return response.data
}

export const extractDocument = async (id: number, selectedFields: string[]): Promise<ExtractionResponse> => {
  const response = await api.post(`/documents/${id}/extract`, {
    selected_fields: selectedFields,
  })
  return response.data
}

export const approveDocument = async (id: number): Promise<Document> => {
  const response = await api.post(`/documents/${id}/approve`)
  return response.data
}

export const rejectDocument = async (id: number, reason?: string): Promise<Document> => {
  const response = await api.post(`/documents/${id}/reject`, { reason })
  return response.data
}

export const escalateDocument = async (id: number, reason?: string): Promise<Document> => {
  const response = await api.post(`/documents/${id}/escalate`, { reason })
  return response.data
}

export const chatWithDocument = async (id: number, query: string): Promise<ChatResponse> => {
  const response = await api.post(`/documents/${id}/chat`, { query })
  return response.data
}

export const getChatHistory = async (id: number): Promise<ChatResponse[]> => {
  const response = await api.get(`/documents/${id}/chat/history`)
  return response.data
}

export const exportDocumentCsv = async (id: number): Promise<Blob> => {
  const response = await api.get(`/documents/${id}/export/csv`, {
    responseType: 'blob',
  })
  return response.data
}

export const exportDocumentMarkdown = async (id: number): Promise<Blob> => {
  const response = await api.get(`/documents/${id}/export/markdown`, {
    responseType: 'blob',
  })
  return response.data
}

export const getDocumentPdf = (id: number): string => {
  return `${API_BASE_URL}/documents/${id}/pdf`
}

export const getDocumentMarkdown = async (id: number): Promise<{ markdown: string; processed_at: string }> => {
  const response = await api.get(`/documents/${id}/markdown`)
  return response.data
}

// Helper function to calculate stats
export const getDocumentStats = async (): Promise<DocumentStats> => {
  const response = await getDocuments()
  const documents = response.documents
  
  const stats = {
    total: documents.length,
    pending: documents.filter(d => ['pending', 'parsing', 'extracting'].includes(d.status)).length,
    completed: documents.filter(d => ['extracted', 'approved'].includes(d.status)).length,
    failed: documents.filter(d => d.status === 'failed').length,
    successful: documents.filter(d => d.status === 'approved').length,
    completionRate: 0,
  }
  
  if (stats.total > 0) {
    stats.completionRate = Math.round((stats.completed / stats.total) * 100)
  }
  
  return stats
}