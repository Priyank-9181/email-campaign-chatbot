import { Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Datasets from './pages/Datasets'
import Chat from './pages/Chat'
import Campaigns from './pages/Campaigns'

export default function App() {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Navbar />
        <main className="flex-1 overflow-auto bg-slate-50 p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/datasets" element={<Datasets />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/campaigns" element={<Campaigns />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
