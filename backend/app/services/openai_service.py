"""
OpenAI GPT-4.1 Chat Service for document-based Q&A with contextual highlighting
"""
import json
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import openai
from openai import OpenAI
import re

from app.core.config import settings
from app.models.document import Document
from app.models.chat_log import ChatLog
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Service for handling OpenAI GPT-4.1 chat interactions with document context.
    Integrates with Landing.AI chunk telemetry for precise PDF highlighting.
    """
    
    def __init__(self):
        """Initialize OpenAI client with API key"""
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info(f"OpenAI client initialized with model: {settings.OPENAI_MODEL}")
    
    def chat_with_document(
        self, 
        db: Session,
        document: Document, 
        query: str,
        user_id: Optional[str] = None,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """
        Chat with a document using GPT-4.1 and return response with highlight mappings.
        
        Args:
            db: Database session
            document: Document object
            query: User's question about the document
            user_id: Optional user identifier
            include_history: Whether to include chat history in context
            
        Returns:
            Dict containing:
                - response: AI response text
                - highlighted_chunks: List of chunk IDs that were referenced
                - highlight_areas: List of PDF bounding boxes for highlighting
                - confidence: Confidence score of the response
        """
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please configure OPENAI_API_KEY.")
        
        if not document.extracted_md and not document.extracted_data:
            raise ValueError("Document has no extracted content for chat.")
        
        try:
            # Prepare document context with chunk metadata
            context = self._prepare_document_context(document)
            
            # Get chat history if requested
            history_context = ""
            if include_history:
                history_context = self._get_chat_history(db, document.id, limit=5)
            
            # Build the prompt for GPT-4.1
            # Using specific prompt structure for GPT-4.1's literal instruction following
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(query, context, history_context)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Parse the response
            result = self._parse_gpt_response(response.choices[0].message.content)
            
            # Map chunk references to PDF bounding boxes
            highlight_areas = self._map_chunks_to_pdf_areas(
                document, 
                result.get('referenced_chunks', [])
            )
            
            # Store chat in database
            chat_log = self._store_chat_log(
                db, 
                document.id, 
                query, 
                result['answer'],
                highlight_areas,
                user_id
            )
            
            return {
                'id': chat_log.id,
                'query': query,
                'response': result['answer'],
                'highlighted_chunks': result.get('referenced_chunks', []),
                'highlight_areas': highlight_areas,
                'confidence': result.get('confidence', 0.0),
                'created_at': chat_log.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in chat_with_document: {str(e)}")
            raise
    
    def _prepare_document_context(self, document: Document) -> str:
        """
        Prepare document content with chunk metadata for context.
        Includes chunk IDs and positions for precise highlighting.
        """
        context_parts = []
        
        # Add document metadata
        context_parts.append(f"Document: {document.filename}")
        context_parts.append(f"Processed: {document.processed_at}")
        context_parts.append("")
        
        # Add extracted content with chunk markers
        if document.extracted_data:
            # Parse the extracted data for chunk information
            extracted_data = document.extracted_data
            if isinstance(extracted_data, str):
                try:
                    extracted_data = json.loads(extracted_data)
                except json.JSONDecodeError:
                    extracted_data = {}
            
            # Add chunk-marked content
            if 'chunks' in extracted_data:
                context_parts.append("=== Document Content (with chunk markers) ===")
                for chunk in extracted_data['chunks']:
                    chunk_id = chunk.get('id', '')
                    chunk_text = chunk.get('text', '')
                    chunk_page = chunk.get('page', 0)
                    
                    context_parts.append(f"[CHUNK_{chunk_id}_PAGE_{chunk_page}]")
                    context_parts.append(chunk_text)
                    context_parts.append(f"[/CHUNK_{chunk_id}]")
                    context_parts.append("")
            elif document.extracted_md:
                # Fallback to markdown if no chunks
                context_parts.append("=== Document Content ===")
                context_parts.append(document.extracted_md)
        elif document.extracted_md:
            context_parts.append("=== Document Content ===")
            context_parts.append(document.extracted_md)
        
        return "\n".join(context_parts)
    
    def _build_system_prompt(self) -> str:
        """
        Build system prompt optimized for GPT-4.1's capabilities.
        Leverages its 1M context window and literal instruction following.
        """
        return """You are an advanced document analysis assistant powered by GPT-4.1.
You have access to the complete content of a document with chunk markers that indicate specific sections.

Your task is to answer questions about the document content accurately and provide references to the specific chunks that support your answer.

CRITICAL INSTRUCTIONS (Follow these literally):
1. Answer ONLY based on the provided document content
2. When citing information, ALWAYS reference the specific chunk IDs
3. Return your response in valid JSON format with the following structure:
{
    "answer": "Your detailed answer to the question",
    "referenced_chunks": ["chunk_id_1", "chunk_id_2", ...],
    "confidence": 0.95,
    "reasoning": "Brief explanation of how you arrived at this answer"
}

4. The confidence score should be between 0.0 and 1.0
5. If you cannot answer from the document, set confidence to 0.0 and explain why
6. Extract chunk IDs from markers like [CHUNK_ABC123_PAGE_1]
7. Be precise and comprehensive in your answers
8. Maintain context awareness across the entire document"""
    
    def _build_user_prompt(self, query: str, context: str, history: str) -> str:
        """
        Build user prompt with query, document context, and chat history.
        """
        prompt_parts = []
        
        if history:
            prompt_parts.append("=== Previous Conversation ===")
            prompt_parts.append(history)
            prompt_parts.append("")
        
        prompt_parts.append("=== Document Context ===")
        prompt_parts.append(context)
        prompt_parts.append("")
        prompt_parts.append("=== User Question ===")
        prompt_parts.append(query)
        prompt_parts.append("")
        prompt_parts.append("Please analyze the document and provide a comprehensive answer in JSON format.")
        
        return "\n".join(prompt_parts)
    
    def _parse_gpt_response(self, content: str) -> Dict[str, Any]:
        """
        Parse GPT-4.1 response and extract structured data.
        """
        try:
            # Try to parse as JSON
            result = json.loads(content)
            
            # Validate required fields
            if 'answer' not in result:
                result['answer'] = content  # Fallback to raw content
            
            # Extract chunk IDs from the response if not properly formatted
            if 'referenced_chunks' not in result:
                # Try to extract chunk references from the text
                chunk_pattern = r'CHUNK_([A-Za-z0-9]+)_PAGE_\d+'
                chunks = re.findall(chunk_pattern, content)
                result['referenced_chunks'] = list(set(chunks))
            
            # Set default confidence if not provided
            if 'confidence' not in result:
                result['confidence'] = 0.8
            
            return result
            
        except json.JSONDecodeError:
            # Fallback for non-JSON response
            logger.warning("GPT response was not valid JSON, using fallback parsing")
            
            # Extract chunk references from plain text
            chunk_pattern = r'CHUNK_([A-Za-z0-9]+)_PAGE_\d+'
            chunks = re.findall(chunk_pattern, content)
            
            return {
                'answer': content,
                'referenced_chunks': list(set(chunks)),
                'confidence': 0.5,
                'reasoning': 'Response parsed from plain text'
            }
    
    def _map_chunks_to_pdf_areas(
        self, 
        document: Document, 
        chunk_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Map chunk IDs to PDF bounding boxes using Landing.AI telemetry.
        
        Returns:
            List of highlight areas with page and bbox coordinates
        """
        highlight_areas = []
        
        if not document.extracted_data:
            return highlight_areas
        
        try:
            extracted_data = document.extracted_data
            if isinstance(extracted_data, str):
                extracted_data = json.loads(extracted_data)
            
            # Get chunk metadata from Landing.AI extraction
            chunks_metadata = extracted_data.get('chunks', [])
            
            for chunk_id in chunk_ids:
                # Find matching chunk metadata
                for chunk in chunks_metadata:
                    if chunk.get('id') == chunk_id:
                        # Extract bounding box information
                        bbox = chunk.get('bbox', None)
                        page = chunk.get('page', 1)
                        
                        if bbox:
                            highlight_areas.append({
                                'page': page,
                                'bbox': bbox,  # [x1, y1, x2, y2] format
                                'chunk_id': chunk_id
                            })
                        break
            
        except Exception as e:
            logger.error(f"Error mapping chunks to PDF areas: {str(e)}")
        
        return highlight_areas
    
    def _get_chat_history(
        self, 
        db: Session, 
        document_id: int, 
        limit: int = 5
    ) -> str:
        """
        Retrieve recent chat history for context.
        """
        try:
            recent_chats = db.query(ChatLog).filter(
                ChatLog.document_id == document_id
            ).order_by(
                ChatLog.created_at.desc()
            ).limit(limit).all()
            
            if not recent_chats:
                return ""
            
            history_parts = []
            for chat in reversed(recent_chats):  # Chronological order
                history_parts.append(f"Q: {chat.query}")
                history_parts.append(f"A: {chat.response}")
                history_parts.append("")
            
            return "\n".join(history_parts)
            
        except Exception as e:
            logger.error(f"Error retrieving chat history: {str(e)}")
            return ""
    
    def _store_chat_log(
        self,
        db: Session,
        document_id: int,
        query: str,
        response: str,
        highlight_areas: List[Dict[str, Any]],
        user_id: Optional[str] = None
    ) -> ChatLog:
        """
        Store chat interaction in database for audit and history.
        """
        try:
            chat_log = ChatLog(
                document_id=document_id,
                query=query,
                response=response,
                highlighted_areas=json.dumps(highlight_areas),
                user_id=user_id or "anonymous",
                model_used=settings.OPENAI_MODEL,
                created_at=datetime.utcnow()
            )
            
            db.add(chat_log)
            db.commit()
            db.refresh(chat_log)
            
            return chat_log
            
        except Exception as e:
            logger.error(f"Error storing chat log: {str(e)}")
            db.rollback()
            raise
    
    def get_chat_history(
        self, 
        db: Session, 
        document_id: int,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get chat history for a document.
        """
        query = db.query(ChatLog).filter(
            ChatLog.document_id == document_id
        ).order_by(ChatLog.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        chats = query.all()
        
        return [
            {
                'id': chat.id,
                'query': chat.query,
                'response': chat.response,
                'highlighted_areas': json.loads(chat.highlighted_areas) if chat.highlighted_areas else [],
                'created_at': chat.created_at.isoformat(),
                'user_id': chat.user_id
            }
            for chat in chats
        ]