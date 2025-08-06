"""
Enhanced markdown processor for Landing.AI output with proper table handling
"""
import re
import json
import csv
from io import StringIO
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import html


class LandingAIMarkdownProcessor:
    """Process Landing.AI markdown output for clean rendering and export"""
    
    @staticmethod
    def clean_markdown_for_display(markdown: str) -> str:
        """
        Clean Landing.AI markdown for display in the UI.
        Removes HTML comments, IDs, and ensures proper table formatting.
        """
        if not markdown:
            return ''
        
        # Step 1: Remove all HTML comments including Landing.AI metadata
        # Pattern matches <!-- any content --> including multiline
        cleaned = re.sub(r'<!--[\s\S]*?-->', '', markdown, flags=re.MULTILINE)
        
        # Step 2: Remove specific ID markers {#id} or data-id attributes
        cleaned = re.sub(r'\{#[^}]+\}', '', cleaned)
        cleaned = re.sub(r'data-id="[^"]*"', '', cleaned)
        
        # Step 3: Clean up arrow symbols that Landing.AI sometimes adds
        cleaned = cleaned.replace('→', '')
        
        # Step 4: Process HTML tables to markdown tables if present
        if '<table>' in cleaned or '<TABLE>' in cleaned.upper():
            cleaned = LandingAIMarkdownProcessor._html_table_to_markdown(cleaned)
        
        # Step 5: Ensure proper table formatting with consistent spacing
        cleaned = LandingAIMarkdownProcessor._normalize_markdown_tables(cleaned)
        
        # Step 6: Clean up excessive whitespace
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'[ \t]+$', '', cleaned, flags=re.MULTILINE)
        
        return cleaned.strip()
    
    @staticmethod
    def _html_table_to_markdown(content: str) -> str:
        """Convert HTML tables to markdown tables"""
        # Find all HTML table blocks
        table_pattern = re.compile(r'<table[^>]*>[\s\S]*?</table>', re.IGNORECASE)
        
        def convert_table(match):
            table_html = match.group(0)
            try:
                soup = BeautifulSoup(table_html, 'html.parser')
                table = soup.find('table')
                if not table:
                    return match.group(0)
                
                rows = []
                
                # Process header rows
                thead = table.find('thead')
                if thead:
                    for tr in thead.find_all('tr'):
                        cells = []
                        for cell in tr.find_all(['th', 'td']):
                            # Handle colspan
                            colspan = int(cell.get('colspan', 1))
                            cell_text = cell.get_text(strip=True)
                            cells.append(cell_text)
                            # Add empty cells for colspan > 1
                            for _ in range(colspan - 1):
                                cells.append('')
                        if cells:
                            rows.append(cells)
                
                # Process body rows
                tbody = table.find('tbody')
                if tbody:
                    for tr in tbody.find_all('tr'):
                        cells = []
                        for cell in tr.find_all(['td', 'th']):
                            cell_text = cell.get_text(strip=True)
                            # Clean up the cell text
                            cell_text = re.sub(r'\s+', ' ', cell_text)
                            cells.append(cell_text)
                        if cells:
                            rows.append(cells)
                
                # If no tbody/thead, process all rows
                if not thead and not tbody:
                    for tr in table.find_all('tr'):
                        cells = []
                        for cell in tr.find_all(['td', 'th']):
                            cell_text = cell.get_text(strip=True)
                            cell_text = re.sub(r'\s+', ' ', cell_text)
                            cells.append(cell_text)
                        if cells:
                            rows.append(cells)
                
                # Convert to markdown table
                if rows:
                    # Ensure all rows have the same number of columns
                    max_cols = max(len(row) for row in rows)
                    for row in rows:
                        while len(row) < max_cols:
                            row.append('')
                    
                    # Build markdown table
                    md_lines = []
                    
                    # First row (header)
                    if rows:
                        md_lines.append('| ' + ' | '.join(rows[0]) + ' |')
                        # Separator
                        md_lines.append('|' + '|'.join([' --- ' for _ in range(max_cols)]) + '|')
                        # Rest of the rows
                        for row in rows[1:]:
                            md_lines.append('| ' + ' | '.join(row) + ' |')
                    
                    return '\n'.join(md_lines)
                
            except Exception as e:
                # If conversion fails, return original
                return match.group(0)
            
            return match.group(0)
        
        # Replace all tables
        content = table_pattern.sub(convert_table, content)
        return content
    
    @staticmethod
    def _normalize_markdown_tables(content: str) -> str:
        """Normalize markdown table formatting"""
        lines = content.split('\n')
        normalized_lines = []
        in_table = False
        
        for i, line in enumerate(lines):
            # Check if this is a table line
            if '|' in line:
                # Clean up the line
                # Remove extra spaces around pipes
                line = re.sub(r'\s*\|\s*', ' | ', line)
                # Ensure line starts and ends with pipe
                if not line.strip().startswith('|'):
                    line = '| ' + line.strip()
                if not line.strip().endswith('|'):
                    line = line.strip() + ' |'
                
                # Check if this is a separator line
                if re.match(r'^\s*\|[\s\-:\|]+\|\s*$', line):
                    # Normalize separator
                    num_cols = line.count('|') - 1
                    line = '|' + ' --- |' * num_cols
                    in_table = True
                elif in_table or (i > 0 and '|' in lines[i-1]):
                    in_table = True
                
                normalized_lines.append(line)
            else:
                if in_table and line.strip() == '':
                    in_table = False
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    @staticmethod
    def extract_clean_csv_data(markdown: str, extracted_data: Optional[str] = None) -> str:
        """
        Extract clean CSV data from markdown and/or extracted data.
        Returns a properly formatted CSV string ready for export.
        """
        csv_rows = []
        
        # First try to extract from markdown tables
        if markdown:
            cleaned_md = LandingAIMarkdownProcessor.clean_markdown_for_display(markdown)
            tables = LandingAIMarkdownProcessor._extract_markdown_tables(cleaned_md)
            
            for table in tables:
                csv_rows.extend(table)
        
        # If we have extracted_data, try to use it as well
        if extracted_data and not csv_rows:
            try:
                data = json.loads(extracted_data) if isinstance(extracted_data, str) else extracted_data
                
                if isinstance(data, dict):
                    # Convert dict to CSV rows
                    headers = list(data.keys())
                    values = [str(v) if v is not None else '' for v in data.values()]
                    csv_rows = [headers, values]
                elif isinstance(data, list) and data:
                    if isinstance(data[0], dict):
                        # List of dicts
                        headers = list(data[0].keys())
                        csv_rows.append(headers)
                        for item in data:
                            row = [str(item.get(h, '')) for h in headers]
                            csv_rows.append(row)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Convert to CSV string
        if csv_rows:
            output = StringIO()
            writer = csv.writer(output)
            writer.writerows(csv_rows)
            return output.getvalue()
        
        return ''
    
    @staticmethod
    def _extract_markdown_tables(content: str) -> List[List[str]]:
        """Extract all tables from markdown content"""
        tables = []
        lines = content.split('\n')
        current_table = []
        in_table = False
        
        for line in lines:
            # Check if line is a table row
            if '|' in line:
                # Skip separator rows
                if re.match(r'^\s*\|[\s\-:\|]+\|\s*$', line):
                    in_table = True
                    continue
                
                if in_table or line.strip().startswith('|'):
                    # Parse table row
                    # Remove leading/trailing pipes and split
                    line = line.strip()
                    if line.startswith('|'):
                        line = line[1:]
                    if line.endswith('|'):
                        line = line[:-1]
                    
                    cells = [cell.strip() for cell in line.split('|')]
                    
                    # Clean cells of any remaining markdown
                    cleaned_cells = []
                    for cell in cells:
                        # Remove bold/italic markers
                        cell = re.sub(r'\*\*([^*]+)\*\*', r'\1', cell)
                        cell = re.sub(r'\*([^*]+)\*', r'\1', cell)
                        cell = re.sub(r'__([^_]+)__', r'\1', cell)
                        cell = re.sub(r'_([^_]+)_', r'\1', cell)
                        # Remove code markers
                        cell = re.sub(r'`([^`]+)`', r'\1', cell)
                        # Clean HTML entities
                        cell = html.unescape(cell)
                        cleaned_cells.append(cell)
                    
                    if cleaned_cells:
                        current_table.append(cleaned_cells)
                        in_table = True
            elif in_table and line.strip() == '':
                # End of table
                if current_table:
                    tables.append(current_table)
                    current_table = []
                in_table = False
        
        # Add last table if exists
        if current_table:
            tables.append(current_table)
        
        return tables
    
    @staticmethod
    def format_for_markdown_export(markdown: str) -> str:
        """
        Format markdown for clean export file.
        Preserves markdown formatting while cleaning Landing.AI artifacts.
        """
        if not markdown:
            return ''
        
        # Clean but preserve markdown formatting
        cleaned = LandingAIMarkdownProcessor.clean_markdown_for_display(markdown)
        
        # Add nice spacing for readability
        lines = cleaned.split('\n')
        formatted_lines = []
        prev_was_table = False
        
        for line in lines:
            is_table = '|' in line
            
            # Add spacing around tables
            if is_table and not prev_was_table:
                if formatted_lines and formatted_lines[-1].strip():
                    formatted_lines.append('')
            elif not is_table and prev_was_table:
                formatted_lines.append('')
            
            formatted_lines.append(line)
            prev_was_table = is_table
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def extract_plain_text(markdown: str) -> str:
        """
        Extract plain text from markdown, removing all formatting.
        """
        if not markdown:
            return ''
        
        # Start with cleaned markdown
        text = LandingAIMarkdownProcessor.clean_markdown_for_display(markdown)
        
        # Extract tables as tab-separated text
        tables = LandingAIMarkdownProcessor._extract_markdown_tables(text)
        table_text = []
        for table in tables:
            for row in table:
                table_text.append('\t'.join(row))
        
        # Remove table markdown from text
        text = re.sub(r'\|[^\n]+\|', '', text, flags=re.MULTILINE)
        
        # Remove markdown formatting
        # Headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # Bold and italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # Images
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
        # Code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # Horizontal rules
        text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
        
        # Clean up whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Add tables back as plain text
        if table_text:
            text = text.strip() + '\n\n' + '\n'.join(table_text)
        
        return text.strip()