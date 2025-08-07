import { useCallback, useState, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation, useQueryClient } from 'react-query'
import { useNavigate } from 'react-router-dom'
import { Upload as UploadIcon, File, X, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { uploadDocument } from '../services/api'

interface FileWithStatus {
  originalFile: File  // The actual File object from react-dropzone
  id: string          // Unique ID for React keys and internal tracking
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress: number
  error?: string
}

export default function Upload() {
  const [files, setFiles] = useState<FileWithStatus[]>([])
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const uploadMutation = useMutation(uploadDocument, {
    onSuccess: (data, variables) => {
      setFiles((prev) =>
        prev.map((f) =>
          f.id === variables.id ? { ...f, status: 'success' as const, progress: 100 } : f
        )
      )
      queryClient.invalidateQueries('documents')
      toast.success(`${variables.file.name} uploaded successfully`)
      
      // Navigate to document review after successful upload
      setTimeout(() => {
        navigate(`/documents/${data.id}`)
      }, 1000)
    },
    onError: (error: any, variables) => {
      console.error('Upload error details:', error)
      let errorMessage = 'Upload failed'
      
      // Handle the error message extraction
      if (error.message) {
        errorMessage = error.message
      }
      
      setFiles((prev) =>
        prev.map((f) =>
          f.id === variables.id
            ? { ...f, status: 'error' as const, error: errorMessage }
            : f
        )
      )
      toast.error(errorMessage)
    },
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      originalFile: file,  // Store the actual File object here
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      status: 'pending' as const,
      progress: 0,
    }))
    setFiles((prev) => [...prev, ...newFiles])

    // Auto-upload files
    newFiles.forEach((fileWithStatus) => {
      setFiles((prev) =>
        prev.map((f) =>
          f.id === fileWithStatus.id ? { ...f, status: 'uploading' as const, progress: 50 } : f
        )
      )
      // Pass both the original File and the unique ID to the mutation
      uploadMutation.mutate({ file: fileWithStatus.originalFile, id: fileWithStatus.id })
    })
  }, [uploadMutation])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    // Remove file size limit to support large PDFs (900MB+)
    // Backend will handle chunking for processing
  })

  const removeFile = (fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId))
  }

  // Handle file rejections
  useEffect(() => {
    if (fileRejections.length > 0) {
      fileRejections.forEach((rejection) => {
        const errors = rejection.errors.map(e => e.message).join(', ')
        toast.error(`File rejected: ${rejection.file.name} - ${errors}`)
      })
    }
  }, [fileRejections])

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Upload Documents</h1>
        <p className="text-gray-400 mt-1">
          Upload PDF documents for agentic extraction and processing
        </p>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`card p-8 border-2 border-dashed transition-colors cursor-pointer ${
          isDragActive
            ? 'border-accent-green bg-accent-green/5'
            : 'border-dark-600 hover:border-dark-500'
        }`}
      >
        <input {...getInputProps()} />
        <div className="text-center">
          <UploadIcon className="mx-auto text-gray-400 mb-4" size={48} />
          {isDragActive ? (
            <p className="text-lg text-accent-green">Drop the files here...</p>
          ) : (
            <>
              <p className="text-lg mb-2">Drag & drop PDF files here</p>
              <p className="text-sm text-gray-400">or click to select files</p>
              <p className="text-xs text-gray-500 mt-4">Supports large PDFs (900MB+) with automatic chunking</p>
            </>
          )}
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6 space-y-3">
          <h3 className="text-lg font-medium">Uploaded Files</h3>
          {files.map((file) => (
            <div key={file.id} className="card p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <File className="text-gray-400" size={20} />
                  <div>
                    <p className="font-medium">{file.originalFile.name}</p>
                    <p className="text-sm text-gray-400">
                      {(file.originalFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {file.status === 'pending' && (
                    <span className="text-sm text-gray-400">Waiting...</span>
                  )}
                  {file.status === 'uploading' && (
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-dark-700 rounded-full h-2">
                        <div
                          className="bg-accent-green h-2 rounded-full transition-all"
                          style={{ width: `${file.progress}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-400">{file.progress}%</span>
                    </div>
                  )}
                  {file.status === 'success' && (
                    <CheckCircle className="text-accent-green" size={20} />
                  )}
                  {file.status === 'error' && (
                    <div className="flex items-center gap-2">
                      <AlertCircle className="text-accent-red" size={20} />
                      <span className="text-sm text-accent-red">{file.error}</span>
                    </div>
                  )}
                  <button
                    onClick={() => removeFile(file.id)}
                    className="p-1 hover:bg-dark-700 rounded transition-colors"
                  >
                    <X size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}