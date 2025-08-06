/**
 * Utility functions for processing and cleaning markdown from Landing.AI
 */

/**
 * Clean Landing.AI markdown output by removing HTML comments and IDs
 * @param markdown Raw markdown from Landing.AI
 * @returns Cleaned markdown suitable for display
 */
export function cleanLandingAIMarkdown(markdown: string): string {
  if (!markdown) return ''
  
  // Remove HTML comments (e.g., <!-- Page 1 -->)
  let cleaned = markdown.replace(/<!--[\s\S]*?-->/g, '')
  
  // Remove ID markers (e.g., {#id123})
  cleaned = cleaned.replace(/\{#[^}]+\}/g, '')
  
  // Clean up excessive whitespace
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n')
  
  // Ensure tables are properly formatted with spacing
  cleaned = cleaned.replace(/(\|.*\|)\n(\|[-:]+\|)/g, '$1\n$2')
  
  // Remove leading/trailing whitespace
  cleaned = cleaned.trim()
  
  return cleaned
}

/**
 * Convert markdown to plain text for export
 * @param markdown Markdown content
 * @returns Plain text without markdown syntax
 */
export function markdownToPlainText(markdown: string): string {
  if (!markdown) return ''
  
  let text = markdown
  
  // Remove headers (# ## ### etc.)
  text = text.replace(/^#{1,6}\s+/gm, '')
  
  // Remove bold and italic markers
  text = text.replace(/(\*\*|__)(.*?)\1/g, '$2')
  text = text.replace(/(\*|_)(.*?)\1/g, '$2')
  
  // Remove links but keep text
  text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
  
  // Remove images
  text = text.replace(/!\[([^\]]*)\]\([^)]+\)/g, '')
  
  // Convert tables to simple text format
  text = text.replace(/\|/g, '\t')
  text = text.replace(/^[\t\s]*[-:]+[\t\s]*$/gm, '')
  
  // Remove code blocks
  text = text.replace(/```[\s\S]*?```/g, '')
  text = text.replace(/`([^`]+)`/g, '$1')
  
  // Remove horizontal rules
  text = text.replace(/^[-*_]{3,}$/gm, '')
  
  // Clean up excessive whitespace
  text = text.replace(/\n{3,}/g, '\n\n')
  text = text.replace(/[ \t]+/g, ' ')
  
  return text.trim()
}

/**
 * Extract table data from markdown for CSV export
 * @param markdown Markdown content
 * @returns Array of table rows
 */
export function extractTablesForCSV(markdown: string): string[][] {
  if (!markdown) return []
  
  const tables: string[][] = []
  const lines = markdown.split('\n')
  let inTable = false
  let currentTable: string[][] = []
  
  for (const line of lines) {
    // Check if line is a table row
    if (line.includes('|')) {
      // Skip separator rows (|---|---|)
      if (line.match(/^[\s|:-]+$/)) {
        inTable = true
        continue
      }
      
      if (inTable || line.trim().startsWith('|')) {
        // Parse table row
        const cells = line
          .split('|')
          .map(cell => cell.trim())
          .filter(cell => cell !== '')
        
        if (cells.length > 0) {
          currentTable.push(cells)
          inTable = true
        }
      }
    } else if (inTable && line.trim() === '') {
      // End of table
      if (currentTable.length > 0) {
        tables.push(...currentTable)
        currentTable = []
      }
      inTable = false
    }
  }
  
  // Add last table if exists
  if (currentTable.length > 0) {
    tables.push(...currentTable)
  }
  
  return tables
}

/**
 * Format markdown for clean display with proper table rendering
 * @param markdown Raw markdown
 * @returns Formatted markdown
 */
export function formatMarkdownForDisplay(markdown: string): string {
  if (!markdown) return ''
  
  // First clean the Landing.AI specific artifacts
  let formatted = cleanLandingAIMarkdown(markdown)
  
  // Ensure proper table formatting
  const lines = formatted.split('\n')
  const formattedLines: string[] = []
  let inTable = false
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const nextLine = lines[i + 1]
    
    // Check if this is a table header
    if (line.includes('|') && nextLine && nextLine.match(/^\|?[\s:-]+\|/)) {
      // Ensure proper spacing around pipes
      const formattedLine = line.replace(/\s*\|\s*/g, ' | ')
      formattedLines.push(formattedLine)
      inTable = true
    } else if (inTable && line.includes('|')) {
      // Format table row
      const formattedLine = line.replace(/\s*\|\s*/g, ' | ')
      formattedLines.push(formattedLine)
    } else {
      formattedLines.push(line)
      if (inTable && line.trim() === '') {
        inTable = false
      }
    }
  }
  
  return formattedLines.join('\n')
}

/**
 * Convert markdown to CSV format
 * @param markdown Markdown content
 * @returns CSV formatted string
 */
export function markdownToCSV(markdown: string): string {
  const tables = extractTablesForCSV(markdown)
  
  if (tables.length === 0) {
    // If no tables, convert plain text to single column CSV
    const plainText = markdownToPlainText(markdown)
    const lines = plainText.split('\n').filter(line => line.trim())
    return lines.map(line => `"${line.replace(/"/g, '""')}"`).join('\n')
  }
  
  // Convert tables to CSV
  return tables
    .map(row => 
      row.map(cell => {
        // Escape quotes and wrap in quotes if needed
        const cleaned = cell.replace(/"/g, '""')
        return cleaned.includes(',') || cleaned.includes('"') || cleaned.includes('\n')
          ? `"${cleaned}"`
          : cleaned
      }).join(',')
    )
    .join('\n')
}