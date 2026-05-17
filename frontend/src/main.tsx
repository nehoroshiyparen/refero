import { createRoot } from 'react-dom/client'
import './index.css'
import { AuthProvider } from './app/providers/AuthProvider'
import { AppRouter } from './app/routes'

createRoot(document.getElementById('root')!).render(
  <AuthProvider>
    <AppRouter />
  </AuthProvider>,
)
