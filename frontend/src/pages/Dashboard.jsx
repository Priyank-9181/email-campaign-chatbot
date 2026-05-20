import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getStats } from '../services/api'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getStats()
      .then((res) => setStats(res.data))
      .catch(() => setError('Could not load stats. Is the backend running?'))
  }, [])

  if (error) {
    return <p className="text-red-600">{error}</p>
  }

  if (!stats) {
    return <p className="text-slate-500">Loading dashboard...</p>
  }

  const cards = [
    { label: 'Datasets', value: stats.datasets, icon: '📦' },
    { label: 'Campaigns', value: stats.campaigns, icon: '✉️' },
    { label: 'Emails Sent', value: stats.emails_sent, icon: '🚀' },
  ]

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold text-slate-800">Dashboard</h2>
      <div className="mb-8 grid gap-4 sm:grid-cols-3">
        {cards.map((card) => (
          <div
            key={card.label}
            className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <span className="text-2xl">{card.icon}</span>
            <p className="mt-2 text-3xl font-bold text-slate-800">{card.value}</p>
            <p className="text-sm text-slate-500">{card.label}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold text-slate-800">Recent Campaigns</h3>
          <Link to="/campaigns" className="text-sm text-indigo-600 hover:underline">
            View all
          </Link>
        </div>
        {stats.recent_campaigns?.length ? (
          <ul className="space-y-2">
            {stats.recent_campaigns.map((c) => (
              <li
                key={c.id}
                className="flex justify-between rounded-lg border border-slate-100 bg-slate-50 px-4 py-2 text-sm"
              >
                <span className="text-slate-700">{c.campaign_name}</span>
                <span className="text-slate-500">{c.status}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">No campaigns yet. Use AI Chat to create one.</p>
        )}
      </div>
    </div>
  )
}
