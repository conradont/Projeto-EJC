import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ParticipantsPage from './pages/ParticipantsPage'
import RegisterPage from './pages/RegisterPage'
import ReportsPage from './pages/ReportsPage'
import EditParticipantPage from './pages/EditParticipantPage'
import LogoPage from './pages/LogoPage'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/participants" element={<ParticipantsPage />} />
          <Route path="/participants/:id/edit" element={<EditParticipantPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/logo" element={<LogoPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
