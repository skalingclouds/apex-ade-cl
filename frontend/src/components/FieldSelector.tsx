import { useState } from 'react'
import { X, Loader, Plus } from 'lucide-react'
import { FieldInfo } from '../services/api'

interface FieldSelectorProps {
  fields: FieldInfo[]
  onSelect: (selectedFields: string[], customFields?: FieldInfo[]) => void
  onClose: () => void
  isLoading: boolean
}

export default function FieldSelector({ fields, onSelect, onClose, isLoading }: FieldSelectorProps) {
  const [selectedFields, setSelectedFields] = useState<string[]>(
    fields.filter(f => f.required).map(f => f.name)
  )
  const [customFields, setCustomFields] = useState<FieldInfo[]>([])
  const [showAddCustom, setShowAddCustom] = useState(false)
  const [customFieldName, setCustomFieldName] = useState('')
  const [customFieldDescription, setCustomFieldDescription] = useState('')

  const toggleField = (fieldName: string) => {
    setSelectedFields(prev =>
      prev.includes(fieldName)
        ? prev.filter(f => f !== fieldName)
        : [...prev, fieldName]
    )
  }

  const handleAddCustomField = () => {
    if (customFieldName.trim()) {
      // Convert to snake_case for consistency
      const fieldName = customFieldName.trim().toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '')
      
      const newField: FieldInfo = {
        name: fieldName,
        type: 'string',
        description: customFieldDescription.trim() || `Custom field: ${customFieldName}`,
        required: false
      }
      
      // Add to custom fields list
      setCustomFields(prev => [...prev, newField])
      
      // Auto-select the new custom field
      setSelectedFields(prev => [...prev, fieldName])
      
      // Reset form
      setCustomFieldName('')
      setCustomFieldDescription('')
      setShowAddCustom(false)
    }
  }

  const removeCustomField = (fieldName: string) => {
    setCustomFields(prev => prev.filter(f => f.name !== fieldName))
    setSelectedFields(prev => prev.filter(f => f !== fieldName))
  }

  const handleSubmit = () => {
    if (selectedFields.length > 0) {
      onSelect(selectedFields, customFields)
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
          <div className="space-y-4">
            {/* AI-Generated Fields */}
            <div>
              <h3 className="text-sm font-semibold text-gray-300 mb-3">AI-Suggested Fields</h3>
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

            {/* Custom Fields Section */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-gray-300">Custom Fields</h3>
                <button
                  onClick={() => setShowAddCustom(true)}
                  className="flex items-center gap-1 text-xs text-accent-green hover:text-accent-green/80 transition-colors"
                >
                  <Plus size={14} />
                  Add Custom Field
                </button>
              </div>

              {/* Custom Field Form */}
              {showAddCustom && (
                <div className="mb-3 p-4 bg-dark-700 rounded-lg border border-accent-green/30">
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-300 mb-1">
                        Field Name
                      </label>
                      <input
                        type="text"
                        value={customFieldName}
                        onChange={(e) => setCustomFieldName(e.target.value)}
                        placeholder="e.g., Customer ID"
                        className="w-full px-3 py-2 bg-dark-800 border border-dark-600 rounded-lg text-sm focus:outline-none focus:border-accent-green"
                        autoFocus
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Will be converted to snake_case (e.g., customer_id)
                      </p>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-300 mb-1">
                        Description (optional)
                      </label>
                      <input
                        type="text"
                        value={customFieldDescription}
                        onChange={(e) => setCustomFieldDescription(e.target.value)}
                        placeholder="Brief description of this field"
                        className="w-full px-3 py-2 bg-dark-800 border border-dark-600 rounded-lg text-sm focus:outline-none focus:border-accent-green"
                      />
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={handleAddCustomField}
                        disabled={!customFieldName.trim()}
                        className="px-3 py-1.5 bg-accent-green text-black text-xs font-medium rounded-lg hover:bg-accent-green/90 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Add Field
                      </button>
                      <button
                        onClick={() => {
                          setShowAddCustom(false)
                          setCustomFieldName('')
                          setCustomFieldDescription('')
                        }}
                        className="px-3 py-1.5 bg-dark-600 text-gray-300 text-xs font-medium rounded-lg hover:bg-dark-500"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Custom Fields List */}
              {customFields.length > 0 && (
                <div className="space-y-3">
                  {customFields.map((field) => (
                    <label
                      key={field.name}
                      className="flex items-start gap-3 p-4 rounded-lg bg-dark-700 hover:bg-dark-600 cursor-pointer transition-colors border border-accent-green/20"
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
                          <span className="text-xs px-2 py-1 bg-accent-green/20 text-accent-green rounded">
                            custom
                          </span>
                        </div>
                        {field.description && (
                          <p className="text-sm text-gray-400 mt-1">{field.description}</p>
                        )}
                      </div>
                      <button
                        onClick={(e) => {
                          e.preventDefault()
                          removeCustomField(field.name)
                        }}
                        className="p-1 hover:bg-dark-800 rounded transition-colors"
                      >
                        <X size={14} className="text-gray-500 hover:text-red-400" />
                      </button>
                    </label>
                  ))}
                </div>
              )}

              {customFields.length === 0 && !showAddCustom && (
                <p className="text-xs text-gray-500 italic">
                  No custom fields added yet. Click "Add Custom Field" to create your own.
                </p>
              )}
            </div>
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