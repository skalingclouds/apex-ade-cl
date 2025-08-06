/**
 * Enhanced markdown utilities for processing Landing.AI output
 */

export function cleanLandingAIMarkdown(markdown: string): string {
  if (!markdown) return ''
  
  // Step 1: Remove all HTML comments including Landing.AI metadata
  // This removes <!-- text, from page X (l=...), with ID ... --> and similar
  let cleaned = markdown.replace(/<!--[\s\S]*?-->/g, '')
  
  // Step 2: Remove ID markers and data-id attributes
  cleaned = cleaned.replace(/\{#[^}]+\}/g, '')
  cleaned = cleaned.replace(/data-id="[^"]*"/g, '')
  
  // Step 3: Remove arrow symbols
  cleaned = cleaned.replace(/→/g, '')
  
  // Step 4: Process HTML tables if present
  if (cleaned.includes('<table>') || cleaned.toUpperCase().includes('<TABLE>')) {
    cleaned = convertHtmlTablesToMarkdown(cleaned)
  }
  
  // Step 5: Normalize table formatting
  cleaned = normalizeMarkdownTables(cleaned)
  
  // Step 6: Clean up excessive whitespace
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n')
  cleaned = cleaned.replace(/[ \t]+$/gm, '')
  
  return cleaned.trim()
}

function convertHtmlTablesToMarkdown(content: string): string {
  // Parse HTML tables and convert to markdown
  const tableRegex = /<table[^>]*>[\s\S]*?<\/table>/gi
  
  return content.replace(tableRegex, (match) => {
    try {
      // Create a temporary DOM element to parse the table
      const parser = new DOMParser()
      const doc = parser.parseFromString(match, 'text/html')
      const table = doc.querySelector('table')
      
      if (!table) return match
      
      const rows: string[][] = []
      
      // Process all rows
      const allRows = table.querySelectorAll('tr')
      allRows.forEach((tr) => {
        const cells: string[] = []
        tr.querySelectorAll('td, th').forEach((cell) => {
          const text = cell.textContent?.trim() || ''
          // Handle colspan
          const colspan = parseInt(cell.getAttribute('colspan') || '1')
          cells.push(text)
          // Add empty cells for colspan > 1
          for (let i = 1; i < colspan; i++) {
            cells.push('')
          }
        })
        if (cells.length > 0) {
          rows.push(cells)
        }
      })
      
      if (rows.length === 0) return match
      
      // Ensure all rows have the same number of columns
      const maxCols = Math.max(...rows.map(row => row.length))
      rows.forEach(row => {
        while (row.length < maxCols) {
          row.push('')
        }
      })
      
      // Build markdown table
      const mdLines: string[] = []
      
      // Header row
      if (rows.length > 0) {
        mdLines.push('| ' + rows[0].join(' | ') + ' |')
        // Separator
        mdLines.push('|' + rows[0].map(() => ' --- ').join('|') + '|')
        // Data rows
        for (let i = 1; i < rows.length; i++) {
          mdLines.push('| ' + rows[i].join(' | ') + ' |')
        }
      }
      
      return '\n' + mdLines.join('\n') + '\n'
    } catch (e) {
      // If parsing fails, return original
      return match
    }
  })
}

function normalizeMarkdownTables(content: string): string {
  const lines = content.split('\n')
  const normalized: string[] = []
  let inTable = false
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    
    if (line.includes('|')) {
      // Clean up spacing around pipes
      let normalizedLine = line.replace(/\s*\|\s*/g, ' | ')
      
      // Ensure line starts and ends with pipe
      if (!normalizedLine.trim().startsWith('|')) {
        normalizedLine = '| ' + normalizedLine.trim()
      }
      if (!normalizedLine.trim().endsWith('|')) {
        normalizedLine = normalizedLine.trim() + ' |'
      }
      
      // Check if this is a separator line
      if (/^\s*\|[\s\-:\|]+\|\s*$/.test(normalizedLine)) {
        // Count columns from previous line
        const prevLine = normalized[normalized.length - 1]
        if (prevLine && prevLine.includes('|')) {
          const colCount = (prevLine.match(/\|/g) || []).length - 1
          normalizedLine = '|' + ' --- |'.repeat(colCount)
        }
        inTable = true
      } else if (inTable || (i > 0 && lines[i - 1].includes('|'))) {
        inTable = true
      }
      
      normalized.push(normalizedLine)
    } else {
      if (inTable && line.trim() === '') {
        inTable = false
      }
      normalized.push(line)
    }
  }
  
  return normalized.join('\n')
}

export function prepareMarkdownForDisplay(markdown: string): string {
  // Clean the markdown first
  const cleaned = cleanLandingAIMarkdown(markdown)
  
  // Additional preparation for React Markdown rendering
  // Ensure proper spacing around tables for better rendering
  const lines = cleaned.split('\n')
  const prepared: string[] = []
  let prevWasTable = false
  
  for (const line of lines) {
    const isTable = line.includes('|')
    
    // Add spacing around tables
    if (isTable && !prevWasTable && prepared.length > 0 && prepared[prepared.length - 1].trim()) {
      prepared.push('')
    }
    
    prepared.push(line)
    
    if (!isTable && prevWasTable) {
      prepared.push('')
    }
    
    prevWasTable = isTable
  }
  
  return prepared.join('\n')
}