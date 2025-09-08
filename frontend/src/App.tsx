import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Analysis } from './pages/Analysis'
import { Results } from './pages/Results'
import { KPI } from './pages/KPI'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/results/:runId" element={<Results />} />
        <Route path="/kpi" element={<KPI />} />
      </Routes>
    </Layout>
  )
}

export default App
