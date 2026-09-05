import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { AuthProvider } from './contexts/AuthContext'

// One view: the app itself.
//
// Upstream boots into a marketing landing and routes to pricing, account,
// legal and OAuth-consent pages, all of which describe a hosted paid service
// operated by someone else. This edition has no plans, no accounts and no
// hosted tier, so those views were removed rather than renamed — a pricing
// table for plans that do not exist is worse than no pricing table.
//
// AuthProvider stays mounted because App reads useAuth(); with no billing
// backend it resolves to a signed-out, unmetered session and every account
// surface inside App stays hidden behind its `billingEnabled` guard.
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)
