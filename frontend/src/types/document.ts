export enum DocumentStatus {
  PENDING = 'PENDING',
  PARSING = 'PARSING',
  PARSED = 'PARSED',
  EXTRACTING = 'EXTRACTING',
  EXTRACTED = 'EXTRACTED',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  ESCALATED = 'ESCALATED',
  FAILED = 'FAILED'
}

export interface Document {
  id: number
  filename: string
  filepath: string
  status: DocumentStatus
  extracted_md?: string
  extracted_data?: any
  error_message?: string
  uploaded_at: string
  processed_at?: string
  updated_at: string
  archived?: boolean
  archived_at?: string
  archived_by?: string
}

export interface DocumentListResponse {
  documents: Document[]
  total: number
  page: number
  pages: number
}

export interface ExportFormat {
  type: 'csv' | 'markdown' | 'text'
  label: string
  icon?: string
}