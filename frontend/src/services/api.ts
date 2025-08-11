import axios from 'axios'

// ------------------------------------------------------------------
// Dynamic configuration via Vite env vars
// ------------------------------------------------------------------
// VITE_API_URL  – full origin of backend (e.g. https://apex-ade-backend.onrender.com)
// VITE_UPLOAD_MODE – 'local' (default) or 'azure'
// ------------------------------------------------------------------

// Remove trailing slash if present so we can safely append routes
const API_ORIGIN =
  (import.meta as any).env?.VITE_API_URL?.replace(/\/$/, '') || ''

export const API_BASE_URL = `${API_ORIGIN}/api/v1`

const UPLOAD_MODE =
  (import.meta as any).env?.VITE_UPLOAD_MODE?.toLowerCase() || 'local'

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
  successful: number
  completionRate: number
}

// -----------------------
//  Upload helpers
// -----------------------
const uploadLocal = async (payload: UploadPayload): Promise<Document> => {
  // Use XMLHttpRequest with proper timeout and progress handling for large files
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    // Build form data
    const formData = new FormData()
    formData.append('file', payload.file)

    xhr.open('POST', `${API_BASE_URL}/documents/upload`)

    // Set a very long timeout for large files (30 minutes)
    xhr.timeout = 30 * 60 * 1000 // 30 minutes in milliseconds

    // Don't set Content-Type header - let browser handle it for multipart

    // Add upload progress tracking
    xhr.upload.onprogress = function (event) {
      if (event.lengthComputable) {
        // Optional: could emit progress updates
      }
    }

    xhr.onload = function () {
      if (xhr.status === 200) {
        try {
          resolve(JSON.parse(xhr.responseText))
        } catch (e) {
          reject(new Error('Invalid response from server'))
        }
      } else if (xhr.status === 413) {
        reject(new Error('File too large. Maximum size is 1GB'))
      } else {
        try {
          const error = JSON.parse(xhr.responseText)
          reject(
            new Error(
              error.detail || error.detail?.[0]?.msg || 'Upload failed'
            )
          )
        } catch (e) {
          reject(new Error(`Upload failed with status ${xhr.status}`))
        }
      }
    }

    xhr.onerror = function () {
      reject(new Error('Network error - check your connection'))
    }

    xhr.ontimeout = function () {
      reject(new Error('Upload timeout - file may be too large or connection too slow'))
    }

    xhr.onabort = function () {
      reject(new Error('Upload was canceled'))
    }

    try {
      xhr.send(formData)
    } catch (e) {
      reject(new Error('Failed to start upload'))
    }
  })
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

// Saved schema types
export interface SavedSchema {
  id: number
  name: string
  description?: string
  fields: FieldInfo[]
  is_active: boolean
  created_at: string
  updated_at: string
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
// (uploadLocal implemented above)

/**
 * Azure Blob upload flow:
 *  1. Ask backend for SAS URL
 *  2. PUT the file to that URL
 *  3. Tell backend to register the blob
 */
const uploadAzure = async (payload: UploadPayload): Promise<Document> => {
  // Step 1 – obtain SAS URL
  const sasResp = await api.post('/uploads/azure-sas', {
    filename: payload.file.name,
    content_type: payload.file.type || 'application/pdf',
    size: payload.file.size,
  })

  const { uploadUrl, blobUrl } = sasResp.data as {
    uploadUrl: string
    blobUrl: string
  }

  // Step 2 – PUT file bytes to Azure
  await new Promise<void>((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('PUT', uploadUrl)
    xhr.setRequestHeader('x-ms-blob-type', 'BlockBlob')
    xhr.setRequestHeader('Content-Type', payload.file.type || 'application/pdf')
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        const pct = (e.loaded / e.total) * 100
        console.log(`Azure upload progress: ${pct.toFixed(2)}%`)
      }
    }
    xhr.onload = () => {
      if (xhr.status === 201 || xhr.status === 200) {
        resolve()
      } else {
        reject(new Error(`Azure upload failed with status ${xhr.status}`))
      }
    }
    xhr.onerror = () => reject(new Error('Azure network error'))
    xhr.ontimeout = () => reject(new Error('Azure upload timeout'))
    xhr.timeout = 30 * 60 * 1000 // 30 min
    xhr.send(payload.file)
  })

  // Step 3 – register blob with backend so it can create Document record
  const registerResp = await api.post('/uploads/register', {
    blob_url: blobUrl,
    filename: payload.file.name,
    size: payload.file.size,
  })
  return registerResp.data
}

// ----------------------------------------------------------
//  Public API – delegates to correct upload implementation
// ----------------------------------------------------------
export const uploadDocument = async (
  payload: UploadPayload
): Promise<Document> => {
  if (UPLOAD_MODE === 'azure') {
    return uploadAzure(payload)
  }
  // default
  return uploadLocal(payload)
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

// Schemas API
export const listSchemas = async (): Promise<SavedSchema[]> => {
  const response = await api.get(`/schemas/`)
  return response.data
}

export const createSchema = async (payload: { name: string; description?: string; fields: FieldInfo[] }): Promise<SavedSchema> => {
  const response = await api.post(`/schemas/`, payload)
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

// Helper for other modules that may need the base URL
export const getApiBaseUrl = (): string => API_BASE_URL
