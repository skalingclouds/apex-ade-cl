import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import DocumentReview from './pages/DocumentReview'
import DocumentManagement from './pages/DocumentManagement'
import Analytics from './pages/Analytics'
import AllDocuments from './pages/AllDocuments'
import NotFound from './pages/NotFound'

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="upload" element={<Upload />} />
          <Route path="documents" element={<AllDocuments />} />
          <Route path="documents/:id" element={<DocumentReview />} />
          <Route path="document-management" element={<DocumentManagement />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
      <Toaster
        position="bottom-right"
        toastOptions={{
          className: '',
          style: {
            background: '#1E1E1E',
            color: '#fff',
            border: '1px solid #323232',
          },
          success: {
            iconTheme: {
              primary: '#10B981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#EF4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </>
  )
}

export default App