import { useState } from 'react'
import { X, Loader } from 'lucide-react'
import { FieldInfo } from '../services/api'

interface FieldSelectorProps {
  fields: FieldInfo[]
  onSelect: (selectedFields: string[]) => void
  onClose: () => void
  isLoading: boolean
}

export default function FieldSelector({ fields, onSelect, onClose, isLoading }: FieldSelectorProps) {
  const [selectedFields, setSelectedFields] = useState<string[]>(
    fields.filter(f => f.required).map(f => f.name)
  )

  const toggleField = (fieldName: string) => {
    setSelectedFields(prev =>
      prev.includes(fieldName)
        ? prev.filter(f => f !== fieldName)
        : [...prev, fieldName]
    )
  }

  const handleSubmit = () => {
    if (selectedFields.length > 0) {
      onSelect(selectedFields)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-dark-800 rounded-lg max-w-2xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-dark-600">
          <div>
            <h2 className="text-xl font-bold">Select Fields to Extract</h2>
            <p className="text-sm text-gray-400 mt-1">
              Choose which fields you want to extract from the document
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Field List */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-3">
            {fields.map((field) => (
              <label
                key={field.name}
                className="flex items-start gap-3 p-4 rounded-lg bg-dark-700 hover:bg-dark-600 cursor-pointer transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selectedFields.includes(field.name)}
                  onChange={() => toggleField(field.name)}
                  className="mt-1 w-4 h-4 text-accent-green bg-dark-800 border-dark-600 rounded focus:ring-accent-green focus:ring-2"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{field.name}</span>
                    <span className="text-xs px-2 py-1 bg-dark-800 rounded">
                      {field.type}
                    </span>
                    {field.required && (
                      <span className="text-xs text-accent-yellow">Required</span>
                    )}
                  </div>
                  {field.description && (
                    <p className="text-sm text-gray-400 mt-1">{field.description}</p>
                  )}
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-dark-600">
          <p className="text-sm text-gray-400">
            {selectedFields.length} field{selectedFields.length !== 1 ? 's' : ''} selected
          </p>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="btn btn-secondary"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={selectedFields.length === 0 || isLoading}
              className="btn btn-primary flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader className="animate-spin" size={16} />
                  Extracting...
                </>
              ) : (
                'Extract Selected Fields'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}