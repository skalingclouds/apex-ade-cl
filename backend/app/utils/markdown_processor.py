"""
Utility functions for processing and cleaning markdown from Landing.AI
"""
import re
import json
from typing import List, Dict, Any


def clean_landing_ai_markdown(markdown: str) -> str:
    """
    Clean Landing.AI markdown output by removing HTML comments and IDs
    
    Args:
        markdown: Raw markdown from Landing.AI
        
    Returns:
        Cleaned markdown suitable for display
    """
    if not markdown:
        return ''
    
    # Remove HTML comments (e.g., <!-- Page 1 -->)
    cleaned = re.sub(r'<!--[\s\S]*?-->', '', markdown)
    
    # Remove ID markers (e.g., {#id123})
    cleaned = re.sub(r'\{#[^}]+\}', '', cleaned)
    
    # Clean up excessive whitespace
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Ensure tables are properly formatted with spacing
    cleaned = re.sub(r'(\|.*\|)\n(\|[-:]+\|)', r'\1\n\2', cleaned)
    
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned


def markdown_to_plain_text(markdown: str) -> str:
    """
    Convert markdown to plain text for export
    
    Args:
        markdown: Markdown content
        
    Returns:
        Plain text without markdown syntax
    """
    if not markdown:
        return ''
    
    text = markdown
    
    # Remove headers (# ## ### etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold and italic markers
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
    
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove images
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
    
    # Convert tables to simple text format
    text = re.sub(r'\|', '\t', text)
    text = re.sub(r'^[\t\s]*[-:]+[\t\s]*$', '', text, flags=re.MULTILINE)
    
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()


def extract_tables_for_csv(markdown: str) -> List[List[str]]:
    """
    Extract table data from markdown for CSV export
    
    Args:
        markdown: Markdown content
        
    Returns:
        List of table rows
    """
    if not markdown:
        return []
    
    tables = []
    lines = markdown.split('\n')
    in_table = False
    current_table = []
    
    for line in lines:
        # Check if line is a table row
        if '|' in line:
            # Skip separator rows (|---|---|)
            if re.match(r'^[\s|:-]+$', line):
                in_table = True
                continue
            
            if in_table or line.strip().startswith('|'):
                # Parse table row
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                
                if cells:
                    current_table.append(cells)
                    in_table = True
        elif in_table and line.strip() == '':
            # End of table
            if current_table:
                tables.extend(current_table)
                current_table = []
            in_table = False
    
    # Add last table if exists
    if current_table:
        tables.extend(current_table)
    
    return tables


def markdown_to_csv_data(markdown: str, extracted_data: str = None) -> List[Dict[str, Any]]:
    """
    Convert markdown and extracted data to CSV-friendly format
    
    Args:
        markdown: Markdown content
        extracted_data: JSON string of extracted data
        
    Returns:
        List of dictionaries suitable for CSV export
    """
    csv_data = []
    
    # First try to use extracted_data if available
    if extracted_data:
        try:
            data = json.loads(extracted_data)
            if isinstance(data, dict):
                # Clean the data - remove markdown syntax from values
                cleaned_data = {}
                for key, value in data.items():
                    if isinstance(value, str):
                        # Remove markdown syntax from the value
                        cleaned_value = markdown_to_plain_text(value)
                        cleaned_data[key] = cleaned_value
                    else:
                        cleaned_data[key] = value
                csv_data = [cleaned_data]
            elif isinstance(data, list):
                # Clean each item in the list
                for item in data:
                    if isinstance(item, dict):
                        cleaned_item = {}
                        for key, value in item.items():
                            if isinstance(value, str):
                                cleaned_value = markdown_to_plain_text(value)
                                cleaned_item[key] = cleaned_value
                            else:
                                cleaned_item[key] = value
                        csv_data.append(cleaned_item)
                    else:
                        csv_data.append({'value': str(item)})
        except (json.JSONDecodeError, TypeError):
            pass
    
    # If no extracted data or parsing failed, extract tables from markdown
    if not csv_data and markdown:
        tables = extract_tables_for_csv(markdown)
        if tables:
            # Assume first row is headers if it exists
            if len(tables) > 1:
                headers = tables[0]
                for row in tables[1:]:
                    row_dict = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            row_dict[header] = row[i]
                        else:
                            row_dict[header] = ''
                    csv_data.append(row_dict)
            else:
                # Single row, create generic headers
                for row in tables:
                    row_dict = {f'Column_{i+1}': cell for i, cell in enumerate(row)}
                    csv_data.append(row_dict)
    
    # If still no data, convert plain text to single column
    if not csv_data and markdown:
        plain_text = markdown_to_plain_text(markdown)
        lines = [line.strip() for line in plain_text.split('\n') if line.strip()]
        csv_data = [{'content': line} for line in lines]
    
    return csv_data


def format_markdown_for_export(markdown: str, include_metadata: bool = True) -> str:
    """
    Format markdown for clean export
    
    Args:
        markdown: Raw markdown
        include_metadata: Whether to include extraction metadata
        
    Returns:
        Formatted markdown for export
    """
    if not markdown:
        return ''
    
    # First clean the Landing.AI specific artifacts
    formatted = clean_landing_ai_markdown(markdown)
    
    # Ensure proper table formatting
    lines = formatted.split('\n')
    formatted_lines = []
    in_table = False
    
    for i, line in enumerate(lines):
        next_line = lines[i + 1] if i + 1 < len(lines) else None
        
        # Check if this is a table header
        if '|' in line and next_line and re.match(r'^\|?[\s:-]+\|', next_line):
            # Ensure proper spacing around pipes
            formatted_line = re.sub(r'\s*\|\s*', ' | ', line)
            formatted_lines.append(formatted_line)
            in_table = True
        elif in_table and '|' in line:
            # Format table row
            formatted_line = re.sub(r'\s*\|\s*', ' | ', line)
            formatted_lines.append(formatted_line)
        else:
            formatted_lines.append(line)
            if in_table and line.strip() == '':
                in_table = False
    
    return '\n'.join(formatted_lines)