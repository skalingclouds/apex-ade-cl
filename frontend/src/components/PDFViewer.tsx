import { useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'
import {
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  RotateCw,
  RotateCcw,
  Maximize2,
  Download
} from 'lucide-react'

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`

interface PDFViewerProps {
  url: string
  highlightAreas?: Array<{ page: number; bbox: number[] }>
  onHighlightsClear?: () => void
}

export default function PDFViewer({ url, highlightAreas = [], onHighlightsClear }: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number>(0)
  const [pageNumber, setPageNumber] = useState<number>(1)
  const [scale, setScale] = useState<number>(1.0)
  const [rotation, setRotation] = useState<number>(0)
  const [pageWidth, setPageWidth] = useState<number>(500)
  
  // Zoom presets
  const zoomLevels = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
  
  const handleZoomIn = () => {
    const currentIndex = zoomLevels.findIndex(level => level >= scale)
    if (currentIndex < zoomLevels.length - 1) {
      setScale(zoomLevels[currentIndex + 1])
    }
  }
  
  const handleZoomOut = () => {
    const currentIndex = zoomLevels.findIndex(level => level >= scale)
    if (currentIndex > 0) {
      setScale(zoomLevels[currentIndex - 1])
    }
  }
  
  const handleRotateClockwise = () => {
    setRotation((prev) => (prev + 90) % 360)
  }
  
  const handleRotateCounterClockwise = () => {
    setRotation((prev) => (prev - 90 + 360) % 360)
  }
  
  const handleFitToWidth = () => {
    // Get container width and set scale accordingly
    const container = document.querySelector('.pdf-container')
    if (container) {
      const containerWidth = container.clientWidth - 40 // Account for padding
      setPageWidth(containerWidth)
      setScale(1.0)
    }
  }
  
  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = url
    link.download = 'document.pdf'
    link.click()
  }
  
  return (
    <div className="flex flex-col h-full">
      {/* Controls Bar */}
      <div className="flex items-center justify-between mb-4 p-3 bg-dark-700 rounded-lg">
        {/* Page Navigation */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPageNumber(Math.max(1, pageNumber - 1))}
            disabled={pageNumber <= 1}
            className="p-2 hover:bg-dark-600 rounded disabled:opacity-50 transition-colors"
            title="Previous Page"
          >
            <ChevronLeft size={18} />
          </button>
          <span className="text-sm min-w-[100px] text-center">
            Page {pageNumber} of {numPages}
          </span>
          <button
            onClick={() => setPageNumber(Math.min(numPages, pageNumber + 1))}
            disabled={pageNumber >= numPages}
            className="p-2 hover:bg-dark-600 rounded disabled:opacity-50 transition-colors"
            title="Next Page"
          >
            <ChevronRight size={18} />
          </button>
        </div>
        
        {/* Zoom Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            disabled={scale <= 0.5}
            className="p-2 hover:bg-dark-600 rounded disabled:opacity-50 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut size={18} />
          </button>
          <span className="text-sm min-w-[60px] text-center">
            {Math.round(scale * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            disabled={scale >= 2.0}
            className="p-2 hover:bg-dark-600 rounded disabled:opacity-50 transition-colors"
            title="Zoom In"
          >
            <ZoomIn size={18} />
          </button>
          <div className="w-px h-6 bg-gray-600 mx-1" />
          <button
            onClick={handleFitToWidth}
            className="p-2 hover:bg-dark-600 rounded transition-colors"
            title="Fit to Width"
          >
            <Maximize2 size={18} />
          </button>
        </div>
        
        {/* Rotation Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleRotateCounterClockwise}
            className="p-2 hover:bg-dark-600 rounded transition-colors"
            title="Rotate Counter-Clockwise"
          >
            <RotateCcw size={18} />
          </button>
          <button
            onClick={handleRotateClockwise}
            className="p-2 hover:bg-dark-600 rounded transition-colors"
            title="Rotate Clockwise"
          >
            <RotateCw size={18} />
          </button>
        </div>
        
        {/* Additional Actions */}
        <div className="flex items-center gap-2">
          {highlightAreas.length > 0 && (
            <button
              onClick={onHighlightsClear}
              className="px-3 py-1 text-xs text-yellow-400 hover:text-yellow-300 transition-colors"
            >
              Clear {highlightAreas.filter(a => a.page === pageNumber).length} highlights
            </button>
          )}
          <button
            onClick={handleDownload}
            className="p-2 hover:bg-dark-600 rounded transition-colors"
            title="Download PDF"
          >
            <Download size={18} />
          </button>
        </div>
      </div>
      
      {/* PDF Display */}
      <div className="flex-1 overflow-auto pdf-container bg-gray-100 rounded-lg p-4">
        <div className="flex justify-center">
          <Document
            file={url}
            onLoadSuccess={({ numPages }) => setNumPages(numPages)}
            className="pdf-document"
            loading={
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-blue"></div>
              </div>
            }
            error={
              <div className="flex flex-col items-center justify-center h-full text-red-400">
                <p>Failed to load PDF</p>
                <button 
                  onClick={() => window.location.reload()}
                  className="mt-2 text-sm underline"
                >
                  Retry
                </button>
              </div>
            }
          >
            <div className="relative inline-block">
              <Page
                pageNumber={pageNumber}
                className="pdf-page shadow-lg"
                width={pageWidth}
                scale={scale}
                rotate={rotation}
                renderTextLayer={true}
                renderAnnotationLayer={true}
              />
              {/* Highlight Overlay */}
              {highlightAreas
                .filter(area => area.page === pageNumber)
                .map((area, index) => {
                  // Calculate position based on scale and rotation
                  const baseStyle = {
                    left: `${(area.bbox[0] / 1000) * 100}%`,
                    top: `${(area.bbox[1] / 1000) * 100}%`,
                    width: `${((area.bbox[2] - area.bbox[0]) / 1000) * 100}%`,
                    height: `${((area.bbox[3] - area.bbox[1]) / 1000) * 100}%`,
                  }
                  
                  // Adjust for rotation if needed
                  const rotationClass = rotation === 0 ? '' : `rotate-${rotation}`
                  
                  return (
                    <div
                      key={index}
                      className={`absolute bg-yellow-400 bg-opacity-30 pointer-events-none border-2 border-yellow-400 ${rotationClass}`}
                      style={{
                        ...baseStyle,
                        transform: `scale(${scale})`,
                        transformOrigin: 'top left'
                      }}
                    />
                  )
                })}
            </div>
          </Document>
        </div>
      </div>
      
      {/* Zoom Indicator */}
      <div className="mt-2 text-center text-xs text-gray-500">
        {scale !== 1.0 && `Zoom: ${Math.round(scale * 100)}%`}
        {rotation !== 0 && ` • Rotation: ${rotation}°`}
      </div>
    </div>
  )
}