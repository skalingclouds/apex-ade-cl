from typing import List, Optional, Dict, Any, Tuple
import re
import json
import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime
import os

from app.schemas.chat import HighlightArea
from app.core.config import settings

# Import landing.ai SDK
try:
    from agentic_doc.parse import parse
    from agentic_doc.common import ParsedDocument, Chunk
except ImportError:
    parse = None
    ParsedDocument = None
    Chunk = None

logger = logging.getLogger(__name__)

@dataclass
class ChatResponseData:
    response: str
    highlighted_areas: Optional[List[HighlightArea]] = None
    fallback: bool = False

class EnhancedChatService:
    """Enhanced service for processing chat queries about documents using Landing AI"""
    
    def __init__(self):
        self.api_key = settings.VISION_AGENT_API_KEY
        
        # Ensure the environment variable is set for the SDK
        if self.api_key:
            os.environ['VISION_AGENT_API_KEY'] = self.api_key
            logger.info(f"EnhancedChatService initialized with API key")
        else:
            logger.warning("No VISION_AGENT_API_KEY found in settings")
    
    async def process_query(
        self,
        document_path: str,
        document_text: str,
        query: str
    ) -> ChatResponseData:
        """Process a chat query and return response with highlights"""
        
        try:
            # Parse the document using Landing AI
            parsed_doc = await self._parse_document(document_path)
            
            if not parsed_doc:
                logger.warning(f"Failed to parse document: {document_path}")
                return self._fallback_response(document_text, query)
            
            # Find relevant chunks based on the query
            relevant_chunks = self._find_relevant_chunks(parsed_doc, query)
            
            if not relevant_chunks:
                return ChatResponseData(
                    response="I couldn't find specific information about that in the document. "
                            "Could you please rephrase your question or ask about something else?",
                    highlighted_areas=None,
                    fallback=True
                )
            
            # Generate response from chunks
            response = self._generate_response_from_chunks(query, relevant_chunks)
            
            # Extract highlight metadata from chunks
            highlighted_areas = self._extract_highlight_metadata(relevant_chunks)
            
            return ChatResponseData(
                response=response,
                highlighted_areas=highlighted_areas,
                fallback=False
            )
            
        except Exception as e:
            logger.error(f"Error processing chat query: {str(e)}")
            # Fall back to simple keyword search
            return self._fallback_response(document_text, query)
    
    async def _parse_document(self, document_path: str) -> Optional[Any]:
        """Parse document using Landing AI SDK"""
        if parse is None:
            return None
        
        try:
            # Run parse in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                parse,
                [document_path],
                None,  # result_save_dir
                None,  # grounding_save_dir
                True,  # include_marginalia
                True   # include_metadata_in_markdown
            )
            
            if result and len(result) > 0:
                return result[0]
            
        except Exception as e:
            logger.error(f"Failed to parse document with Landing AI: {str(e)}")
        
        return None
    
    def _find_relevant_chunks(self, parsed_doc: Any, query: str) -> List[Any]:
        """Find chunks relevant to the query"""
        if not hasattr(parsed_doc, 'chunks'):
            return []
        
        keywords = self._extract_keywords(query)
        relevant_chunks = []
        
        for chunk in parsed_doc.chunks:
            # Check if chunk has text content
            if hasattr(chunk, 'content') and chunk.content:
                content_lower = chunk.content.lower()
                
                # Score chunk based on keyword matches
                score = sum(1 for keyword in keywords if keyword in content_lower)
                
                if score > 0:
                    relevant_chunks.append((score, chunk))
        
        # Sort by score and return top chunks
        relevant_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in relevant_chunks[:5]]  # Top 5 chunks
    
    def _generate_response_from_chunks(self, query: str, chunks: List[Any]) -> str:
        """Generate response based on relevant chunks"""
        if not chunks:
            return "I couldn't find information about that in the document."
        
        response = "Based on the document, here's what I found:\n\n"
        
        for i, chunk in enumerate(chunks[:3], 1):  # Limit to top 3 chunks
            if hasattr(chunk, 'content'):
                # Clean up the content
                content = chunk.content.strip()
                if content:
                    response += f"{i}. {content}\n\n"
        
        return response.strip()
    
    def _extract_highlight_metadata(self, chunks: List[Any]) -> List[HighlightArea]:
        """Extract highlight metadata from chunks"""
        highlights = []
        
        for chunk in chunks:
            try:
                # Check if chunk has bounding box information
                if hasattr(chunk, 'grounding') and chunk.grounding:
                    grounding = chunk.grounding
                    
                    # Extract page and bbox from grounding
                    if hasattr(grounding, 'page_num') and hasattr(grounding, 'bboxes'):
                        page = grounding.page_num
                        
                        # Process each bounding box
                        for bbox in grounding.bboxes:
                            if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
                                highlights.append(HighlightArea(
                                    page=page,
                                    bbox=[float(bbox[0]), float(bbox[1]), 
                                          float(bbox[2]), float(bbox[3])]
                                ))
                            elif hasattr(bbox, 'x1') and hasattr(bbox, 'y1'):
                                # Handle object-based bbox
                                highlights.append(HighlightArea(
                                    page=page,
                                    bbox=[float(bbox.x1), float(bbox.y1),
                                          float(bbox.x2), float(bbox.y2)]
                                ))
                
                # Alternative: check for direct bbox attributes
                elif hasattr(chunk, 'page') and hasattr(chunk, 'bbox'):
                    bbox = chunk.bbox
                    if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
                        highlights.append(HighlightArea(
                            page=chunk.page,
                            bbox=[float(bbox[0]), float(bbox[1]),
                                  float(bbox[2]), float(bbox[3])]
                        ))
                        
            except Exception as e:
                logger.warning(f"Failed to extract highlight from chunk: {str(e)}")
                continue
        
        return highlights
    
    def _fallback_response(self, document_text: str, query: str) -> ChatResponseData:
        """Fallback to simple keyword search when Landing AI is unavailable"""
        logger.info("Using fallback keyword search for chat query")
        
        # Simple keyword-based search
        keywords = self._extract_keywords(query)
        sentences = re.split(r'[.!?]\s+', document_text)
        
        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in keywords):
                relevant_sentences.append(sentence.strip())
        
        if not relevant_sentences:
            return ChatResponseData(
                response="I couldn't find specific information about that in the document. "
                        "Could you please rephrase your question or ask about something else?",
                highlighted_areas=None,
                fallback=True
            )
        
        response = "Based on the document:\n\n"
        for i, sentence in enumerate(relevant_sentences[:3], 1):
            response += f"{i}. {sentence}\n\n"
        
        # Simple highlight generation for fallback
        # Since we don't have PDF coordinates, we'll return empty highlights
        # but log the issue
        logger.warning("Highlight mapping failed in fallback mode - returning response without highlights")
        
        return ChatResponseData(
            response=response.strip(),
            highlighted_areas=None,
            fallback=True
        )
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query"""
        # Remove common words (simple stopword removal)
        stopwords = {'what', 'is', 'the', 'of', 'in', 'a', 'an', 'and', 'or', 
                    'but', 'for', 'with', 'on', 'at', 'to', 'from', 'how',
                    'when', 'where', 'who', 'which', 'tell', 'me', 'about',
                    'can', 'you', 'please', 'find', 'show', 'give'}
        
        # Clean and split query
        words = re.findall(r'\w+', query.lower())
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        return keywords