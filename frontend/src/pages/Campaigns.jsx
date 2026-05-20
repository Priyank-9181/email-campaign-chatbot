import { useCallback, useEffect, useState } from 'react'
import CampaignCard from '../components/CampaignCard'
import {
  deleteCampaign,
  getCampaignLogs,
  getCampaigns,
  sendCampaign,
} from '../services/api'

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([])
  const [preview, setPreview] = useState(null)
  const [logs, setLogs] = useState(null)
  const [sendingId, setSendingId] = useState(null)

  const load = useCallback(() => {
    getCampaigns().then((res) => setCampaigns(res.data)).catch(() => {})
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleSend = async (id) => {
    setSendingId(id)
    try {
      const res = await sendCampaign(id)
      const { success, failed, hint, message } = res.data
      if (failed > 0) {
        const lines = [message || `Sent: ${success}, Failed: ${failed}`]
        if (hint) lines.push('', hint)
        alert(lines.join('\n'))
      }
      load()
    } catch (e) {
      alert(e.response?.data?.detail || 'Send failed. Check SMTP settings in .env')
    } finally {
      setSendingId(null)
    }
  }

  const handleLogs = async (campaign) => {
    const res = await getCampaignLogs(campaign.id)
    setLogs({ campaign, items: res.data })
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this campaign?')) return
    await deleteCampaign(id)
    load()
  }

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold text-slate-800">Campaigns</h2>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {campaigns.map((c) => (
          <CampaignCard
            key={c.id}
            campaign={c}
            onSend={handleSend}
            onView={setPreview}
            onLogs={handleLogs}
            onDelete={handleDelete}
            sending={sendingId === c.id}
          />
        ))}
      </div>
      {!campaigns.length && (
        <p className="text-slate-500">No campaigns yet. Create one via AI Chat.</p>
      )}

      {preview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-400/40 p-4">
          <div className="max-h-[80vh] w-full max-w-2xl overflow-auto rounded-xl border border-slate-200 bg-white p-6 shadow-xl">
            <div className="mb-4 flex justify-between">
              <h3 className="font-semibold text-slate-800">{preview.campaign_name}</h3>
              <button type="button" onClick={() => setPreview(null)} className="text-slate-500 hover:text-slate-700">
                Close
              </button>
            </div>
            <p className="mb-2 text-sm text-slate-600">Subject: {preview.subject}</p>
            <div
              className="prose prose-slate max-w-none rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm"
              dangerouslySetInnerHTML={{ __html: preview.email_body }}
            />
          </div>
        </div>
      )}

      {logs && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-400/40 p-4">
          <div className="max-h-[80vh] w-full max-w-lg overflow-auto rounded-xl border border-slate-200 bg-white p-6 shadow-xl">
            <div className="mb-4 flex justify-between">
              <h3 className="font-semibold text-slate-800">Send logs — {logs.campaign.campaign_name}</h3>
              <button type="button" onClick={() => setLogs(null)} className="text-slate-500 hover:text-slate-700">
                Close
              </button>
            </div>
            {logs.items.length ? (
              <ul className="space-y-2 text-sm">
                {logs.items.map((log) => (
                  <li key={log.id} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
                    <span className={log.status === 'success' ? 'text-emerald-700' : 'text-red-600'}>
                      {log.status}
                    </span>
                    {' — '}
                    {log.recipient_email}
                    {log.error_message && (
                      <p className="mt-1 text-xs text-red-600">{log.error_message}</p>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-slate-500">No send logs yet.</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
