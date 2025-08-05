from typing import List, Optional
import re
from dataclasses import dataclass

from app.schemas.chat import HighlightArea

@dataclass
class ChatResponseData:
    response: str
    highlighted_areas: Optional[List[HighlightArea]] = None
    fallback: bool = False

class ChatService:
    """Service for processing chat queries about documents"""
    
    async def process_query(
        self,
        document_path: str,
        document_text: str,
        query: str
    ) -> ChatResponseData:
        """Process a chat query and return response with highlights"""
        
        # Handle empty document text
        if not document_text:
            return ChatResponseData(
                response="The document appears to be empty or has not been processed yet. "
                        "Please ensure the document has been successfully extracted before using chat.",
                highlighted_areas=[],
                fallback=True
            )
        
        # For MVP, we'll implement a simple keyword-based search
        # In production, this would use an LLM or more sophisticated NLP
        
        # Convert query to lowercase for case-insensitive search
        query_lower = query.lower()
        doc_text_lower = document_text.lower()
        
        # Find relevant sections in the document
        relevant_sections = self._find_relevant_sections(document_text, query)
        
        if not relevant_sections:
            return ChatResponseData(
                response="I couldn't find specific information about that in the document. "
                        "Could you please rephrase your question or ask about something else?",
                highlighted_areas=None,
                fallback=True
            )
        
        # Generate response based on found sections
        response = self._generate_response(query, relevant_sections)
        
        # Calculate highlight areas (simplified for MVP)
        # In production, this would map to actual PDF coordinates
        highlighted_areas = self._calculate_highlights(document_text, relevant_sections)
        
        return ChatResponseData(
            response=response,
            highlighted_areas=highlighted_areas
        )
    
    def _find_relevant_sections(self, document_text: str, query: str) -> List[str]:
        """Find sections of the document relevant to the query"""
        # Simple keyword extraction
        keywords = self._extract_keywords(query)
        
        # Split document into sentences
        sentences = re.split(r'[.!?]\s+', document_text)
        
        relevant_sections = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if any keyword is in the sentence
            if any(keyword in sentence_lower for keyword in keywords):
                relevant_sections.append(sentence.strip())
        
        # Return top 3 most relevant sections
        return relevant_sections[:3]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query"""
        # Remove common words (simple stopword removal)
        stopwords = {'what', 'is', 'the', 'of', 'in', 'a', 'an', 'and', 'or', 
                    'but', 'for', 'with', 'on', 'at', 'to', 'from', 'how',
                    'when', 'where', 'who', 'which', 'tell', 'me', 'about'}
        
        words = query.lower().split()
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        return keywords
    
    def _generate_response(self, query: str, relevant_sections: List[str]) -> str:
        """Generate a response based on the query and relevant sections"""
        if not relevant_sections:
            return "I couldn't find information about that in the document."
        
        # Simple response generation
        response = f"Based on the document, here's what I found about your query:\n\n"
        
        for i, section in enumerate(relevant_sections, 1):
            response += f"{i}. {section}\n\n"
        
        return response.strip()
    
    def _calculate_highlights(
        self, 
        document_text: str, 
        relevant_sections: List[str]
    ) -> List[HighlightArea]:
        """Calculate highlight areas for relevant sections"""
        # This is a simplified version
        # In production, you'd map text positions to PDF coordinates
        
        highlights = []
        for section in relevant_sections:
            # Find position of section in document
            position = document_text.find(section)
            if position != -1:
                # Simplified highlight calculation
                # Assume each character is ~10 pixels wide and lines are 20 pixels high
                char_width = 10
                line_height = 20
                chars_per_line = 80
                
                line_number = position // chars_per_line
                char_in_line = position % chars_per_line
                
                # Calculate bounding box [x1, y1, x2, y2]
                x1 = char_in_line * char_width
                y1 = line_number * line_height
                x2 = x1 + len(section) * char_width
                y2 = y1 + line_height
                
                highlights.append(HighlightArea(
                    page=0,  # Simplified - assume single page
                    bbox=[x1, y1, x2, y2]
                ))
        
        return highlights