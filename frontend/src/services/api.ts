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
    
    // Extract error information from custom error response
    if (error.response?.data?.error) {
      const customError = new Error(error.response.data.error.message || error.message) as any
      customError.errorInfo = error.response.data.error
      customError.retryAllowed = error.response.data.retry_allowed
      customError.escalationAvailable = error.response.data.escalation_available
      return Promise.reject(customError)
    }
    
    return Promise.reject(error)
  }
)

// Document types
export interface Document {
  id: number
  filename: string
  filepath: string
  status: 'PENDING' | 'PARSING' | 'PARSED' | 'EXTRACTING' | 'EXTRACTED' | 'APPROVED' | 'REJECTED' | 'ESCALATED' | 'FAILED'
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
  bbox: number[]  // [x1, y1, x2, y2] bounding box coordinates
}

// Upload payload interface
interface UploadPayload {
  file: File
  id: string
}

// API functions
export const uploadDocument = async (payload: UploadPayload): Promise<Document> => {
  console.log('=== UPLOAD DEBUG ===')
  console.log('File:', payload.file)
  console.log('File name:', payload.file.name)
  console.log('File type:', payload.file.type)
  console.log('File size:', payload.file.size)
  
  // Create FormData and verify it's not being modified
  const formData = new FormData()
  formData.append('file', payload.file)
  
  // Log FormData to ensure it contains the file
  console.log('FormData entries:')
  for (let [key, value] of formData.entries()) {
    console.log(`  ${key}:`, value)
    console.log(`  Value type:`, typeof value)
    console.log(`  Is File:`, value instanceof File)
  }
  
  // Check if FormData is being overridden
  console.log('FormData constructor:', FormData)
  console.log('FormData.prototype:', FormData.prototype)
  
  // Use XMLHttpRequest with proper timeout and progress handling for large files
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    
    // Log the actual request
    const originalSend = xhr.send
    xhr.send = function(data: any) {
      console.log('XHR send called with:', data)
      console.log('Data type:', typeof data)
      console.log('Is FormData:', data instanceof FormData)
      console.log('File size in MB:', payload.file.size / (1024 * 1024))
      return originalSend.call(this, data)
    }
    
    xhr.open('POST', `${API_BASE_URL}/documents/upload`)
    
    // Set a very long timeout for large files (30 minutes)
    xhr.timeout = 30 * 60 * 1000 // 30 minutes in milliseconds
    
    // Don't set Content-Type header - let browser handle it for multipart
    
    // Add upload progress tracking
    xhr.upload.onprogress = function(event) {
      if (event.lengthComputable) {
        const percentComplete = (event.loaded / event.total) * 100
        console.log(`Upload progress: ${percentComplete.toFixed(2)}%`)
        // You could emit this progress to update UI if needed
      }
    }
    
    xhr.onload = function() {
      console.log('Response status:', xhr.status)
      console.log('Response:', xhr.responseText)
      
      if (xhr.status === 200) {
        try {
          resolve(JSON.parse(xhr.responseText))
        } catch (e) {
          console.error('Failed to parse response:', e)
          reject(new Error('Invalid response from server'))
        }
      } else if (xhr.status === 413) {
        reject(new Error('File too large. Maximum size is 1GB'))
      } else {
        try {
          const error = JSON.parse(xhr.responseText)
          reject(new Error(error.detail || error.detail?.[0]?.msg || 'Upload failed'))
        } catch (e) {
          reject(new Error(`Upload failed with status ${xhr.status}`))
        }
      }
    }
    
    xhr.onerror = function() {
      console.error('XHR error event fired')
      reject(new Error('Network error - check your connection'))
    }
    
    xhr.ontimeout = function() {
      console.error('XHR timeout after 30 minutes')
      reject(new Error('Upload timeout - file may be too large or connection too slow'))
    }
    
    xhr.onabort = function() {
      console.error('XHR aborted')
      reject(new Error('Upload was canceled'))
    }
    
    console.log('Sending FormData with file:', payload.file.name)
    console.log('File size:', payload.file.size, 'bytes')
    
    try {
      xhr.send(formData)
    } catch (e) {
      console.error('Failed to send request:', e)
      reject(new Error('Failed to start upload'))
    }
  })
}

export const getDocuments = async (status?: string): Promise<DocumentListResponse> => {
  const params = status ? { status } : {}
  const response = await api.get('/documents/', { params })
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

export const getParsedFields = async (id: number): Promise<ParseResponse> => {
  const response = await api.get(`/documents/${id}/parsed-fields`)
  return response.data
}

export const extractDocument = async (
  id: number, 
  selectedFields: string[], 
  customFields?: FieldInfo[]
): Promise<ExtractionResponse> => {
  const response = await api.post(`/documents/${id}/process`, {
    selected_fields: selectedFields,
    custom_fields: customFields || []
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

export const exportDocumentText = async (id: number): Promise<Blob> => {
  const response = await api.get(`/documents/${id}/export/text`, {
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
export const retryExtraction = async (id: number): Promise<ExtractionResponse> => {
  const response = await api.post(`/documents/${id}/retry`)
  return response.data
}

export const getDocumentStats = async (): Promise<DocumentStats> => {
  const response = await getDocuments()
  const documents = response.documents
  
  const stats = {
    total: documents.length,
    pending: documents.filter(d => ['PENDING', 'PARSING', 'EXTRACTING'].includes(d.status)).length,
    completed: documents.filter(d => ['EXTRACTED', 'APPROVED'].includes(d.status)).length,
    failed: documents.filter(d => d.status === 'FAILED').length,
    successful: documents.filter(d => d.status === 'APPROVED').length,
    completionRate: 0,
  }
  
  if (stats.total > 0) {
    stats.completionRate = Math.round((stats.completed / stats.total) * 100)
  }
  
  return stats
}

// Default export for api instance
export default api