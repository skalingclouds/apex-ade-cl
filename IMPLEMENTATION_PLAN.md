# Implementation Plan: Document Management & Chat Interface Features

## Phase 1: Document Management UI/UX Improvements

### 1.1 Create Document Management Page

#### Backend Requirements:
- **New Endpoint**: `GET /api/v1/documents/by-status` 
  - Query params: `status` (approved|rejected|escalated), `page`, `limit`
  - Returns paginated list of documents by status
  
- **Bulk Operations Endpoint**: `DELETE /api/v1/documents/bulk`
  - Accepts array of document IDs
  - Soft delete or move to archive
  
- **Individual Delete**: `DELETE /api/v1/documents/{id}`
  - Soft delete with status change to 'ARCHIVED'

#### Frontend Components:

**1. DocumentManagementPage.tsx**
```typescript
interface DocumentManagementPageProps {
  // Features:
  - Tab navigation (Approved | Rejected | Escalated)
  - Document list with checkboxes for selection
  - Bulk actions toolbar (Delete Selected, Select All)
  - Individual delete buttons
  - Click handler for document preview
}
```

**2. DocumentPreviewModal.tsx**
```typescript
interface DocumentPreviewModalProps {
  documentId: number
  onClose: () => void
  // Features:
  - Split view: PDF on left, extracted content on right
  - Reuses existing PDFViewer component
  - Shows markdown content with proper formatting
  - Export buttons (CSV, MD, TXT)
  - Close button
}
```

### 1.2 Implementation Steps:

1. **Database Schema Update**:
```sql
ALTER TABLE documents ADD COLUMN archived BOOLEAN DEFAULT FALSE;
ALTER TABLE documents ADD COLUMN archived_at TIMESTAMP;
ALTER TABLE documents ADD COLUMN archived_by VARCHAR(255);
```

2. **Backend Services**:
- Create `DocumentManagementService` for bulk operations
- Add soft delete logic to preserve audit trail
- Implement pagination for large document lists

3. **Frontend Router Update**:
```tsx
<Route path="/documents/manage" element={<DocumentManagementPage />} />
```

4. **Sidebar Navigation Update**:
- Add "Manage Documents" menu item with badge showing counts
- Sub-items: Approved (X), Rejected (Y), Escalated (Z)

---

## Phase 2: Chat Interface with PDF Contextual Highlighting

### 2.1 Backend Implementation

#### OpenAI Integration Service

**File**: `backend/app/services/openai_chat_service.py`
```python
class OpenAIChatService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def process_query(
        self, 
        query: str, 
        document_context: str,
        landing_ai_chunks: List[Dict]  # From Landing.AI parse
    ) -> ChatResponse:
        # 1. Build context from document
        # 2. Query OpenAI with context
        # 3. Extract references from response
        # 4. Map references to Landing.AI chunks
        # 5. Return response with highlight coordinates
```

#### Landing.AI Integration for Highlights

Landing.AI provides chunk-level information with bounding boxes:
```python
# From Landing.AI parse result:
chunk = {
    "text": "content...",
    "page": 0,
    "bbox": {
        "left": 0.123,
        "top": 0.456,
        "right": 0.789,
        "bottom": 0.234
    }
}
```

#### API Endpoints

**1. Chat Endpoint**: `POST /api/v1/documents/{id}/chat`
```python
@router.post("/{document_id}/chat")
async def chat_with_document(
    document_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    # 1. Get document and its parsed chunks
    # 2. Process query with OpenAI
    # 3. Map response to highlights
    # 4. Store chat log
    # 5. Return response with highlights
```

**Response Schema**:
```python
class ChatResponse(BaseModel):
    answer: str
    highlights: Optional[List[HighlightArea]]
    fallback: bool = False
    message_id: int

class HighlightArea(BaseModel):
    page: int
    bbox: List[float]  # [x1, y1, x2, y2] normalized 0-1
    text: Optional[str]  # Matched text snippet
```

### 2.2 Database Schema

```sql
-- Chat logs table
CREATE TABLE chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    user_query TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    highlights JSON,  -- Store highlight metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fallback BOOLEAN DEFAULT FALSE,
    processing_time_ms INTEGER,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- Index for faster queries
CREATE INDEX idx_chat_logs_document ON chat_logs(document_id);
```

### 2.3 Frontend Implementation

#### Enhanced Chat Component

**File**: `frontend/src/components/ChatEnhanced.tsx`
```typescript
interface ChatEnhancedProps {
  documentId: number
  onHighlight: (areas: HighlightArea[]) => void
  documentStatus: string
}

// Features:
// - Real-time message streaming
// - Highlight synchronization with PDF
// - Message history
// - Typing indicators
// - Error recovery with retry
// - Disabled state for rejected documents
```

#### PDF Highlight Integration

**Update**: `frontend/src/components/PDFViewer.tsx`
```typescript
// Add highlight overlay support
interface HighlightArea {
  page: number
  bbox: [number, number, number, number]  // Normalized coordinates
  color?: string
  opacity?: number
  onClick?: () => void
}

// Render highlights as overlay divs
// Support multiple highlight colors (chat vs search)
// Click handlers for highlight interaction
```

### 2.4 Implementation Workflow

1. **User sends chat query** → Frontend sends to backend
2. **Backend processes**:
   - Retrieves document and Landing.AI chunks
   - Builds context from extracted markdown
   - Queries OpenAI with context
   - Matches response segments to chunks
   - Returns response with highlight coordinates
3. **Frontend displays**:
   - Shows AI response in chat
   - Highlights relevant PDF sections
   - Stores in message history
4. **Error handling**:
   - Retry logic for API failures
   - Fallback responses without highlights
   - User notification of issues

### 2.5 OpenAI Configuration

**Environment Variables** (`.env`):
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7
```

**Prompt Template**:
```python
DOCUMENT_QA_PROMPT = """
You are an AI assistant helping users understand a document.

Document Content:
{document_content}

Extracted Data:
{extracted_data}

User Question: {query}

Instructions:
1. Answer based solely on the document content
2. Quote relevant sections when possible
3. If the answer isn't in the document, say so clearly
4. Be concise and accurate

Answer:
"""
```

---

## Phase 3: Integration & Testing

### 3.1 Integration Points

1. **Chat + PDF Viewer**:
   - Bidirectional communication
   - Highlight persistence during chat session
   - Clear highlights on new query

2. **Document Management + Chat History**:
   - Show chat count in document list
   - Export chat logs with document
   - Archive chats with documents

### 3.2 Testing Strategy

**Backend Tests**:
```python
# test_chat_service.py
- test_openai_query_with_context()
- test_highlight_mapping_from_chunks()
- test_chat_log_storage_and_retry()
- test_fallback_response_handling()
```

**Frontend Tests**:
```typescript
// ChatEnhanced.test.tsx
- renders chat interface correctly
- sends queries and displays responses
- highlights PDF on response
- disables on rejected status
- handles errors gracefully
```

### 3.3 Performance Considerations

1. **Chunk Indexing**: Pre-index Landing.AI chunks for faster search
2. **Response Caching**: Cache frequent queries per document
3. **Highlight Optimization**: Batch highlight rendering
4. **Chat History**: Implement virtual scrolling for long conversations

---

## Implementation Timeline

### Week 1: Document Management
- Day 1-2: Backend endpoints and database updates
- Day 3-4: Frontend management page and modal
- Day 5: Testing and refinement

### Week 2: Chat Interface Backend
- Day 1-2: OpenAI service integration
- Day 3: Chat endpoint and highlight mapping
- Day 4: Database schema and chat log storage
- Day 5: Backend testing

### Week 3: Chat Interface Frontend
- Day 1-2: Enhanced chat component
- Day 3: PDF highlight integration
- Day 4: Error handling and edge cases
- Day 5: Integration testing

### Week 4: Polish & Deployment
- Day 1-2: Performance optimization
- Day 3: Security review
- Day 4: Documentation
- Day 5: Deployment preparation

---

## Security Considerations

1. **API Key Management**:
   - Store OpenAI key securely
   - Never expose to frontend
   - Implement rate limiting

2. **Input Validation**:
   - Sanitize chat queries
   - Validate document access permissions
   - Prevent prompt injection

3. **Data Privacy**:
   - Don't send sensitive data to OpenAI
   - Log minimal PII
   - Implement data retention policies

---

## Success Metrics

1. **Document Management**:
   - Bulk operations complete < 2 seconds
   - Preview modal loads < 1 second
   - Zero data loss on deletion

2. **Chat Interface**:
   - Response time < 3 seconds
   - Highlight accuracy > 95%
   - Chat storage success rate > 99.9%

3. **User Experience**:
   - Intuitive navigation
   - Clear visual feedback
   - Graceful error handling

---

## Dependencies Required

### Backend:
```txt
openai==1.3.0
redis==4.5.0  # For caching
tenacity==8.2.0  # For retry logic
```

### Frontend:
```json
{
  "@headlessui/react": "^1.7.0",  // For modals
  "react-intersection-observer": "^9.5.0",  // For virtual scrolling
  "framer-motion": "^10.0.0"  // For animations
}
```

---

## Notes for Implementation

1. **Landing.AI Chunks**: The SDK provides chunk-level data with bounding boxes - use this for precise highlighting
2. **OpenAI Context Window**: Limit document context to fit within token limits
3. **Highlight Colors**: Use different colors for different types (chat vs search)
4. **Mobile Responsiveness**: Ensure modal and chat work on mobile devices
5. **Accessibility**: Add ARIA labels and keyboard navigation

This plan provides a complete roadmap for implementing both requested features with proper integration, testing, and deployment considerations.