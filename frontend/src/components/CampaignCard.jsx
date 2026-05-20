export default function CampaignCard({ campaign, onSend, onView, onLogs, onDelete, sending }) {
  const statusColors = {
    draft: 'bg-amber-100 text-amber-800',
    sent: 'bg-emerald-100 text-emerald-800',
    failed: 'bg-red-100 text-red-800',
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-start justify-between gap-2">
        <h3 className="font-semibold text-slate-800">{campaign.campaign_name}</h3>
        <span className={`rounded-full px-2 py-0.5 text-xs ${statusColors[campaign.status] || statusColors.draft}`}>
          {campaign.status}
        </span>
      </div>
      <p className="mb-4 line-clamp-1 text-sm text-slate-600">{campaign.subject}</p>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => onView(campaign)}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-50"
        >
          Preview
        </button>
        <button
          type="button"
          onClick={() => onLogs(campaign)}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-50"
        >
          Logs
        </button>
        {campaign.status === 'draft' && (
          <button
            type="button"
            disabled={sending}
            onClick={() => onSend(campaign.id)}
            className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {sending ? 'Sending...' : 'Send'}
          </button>
        )}
        <button
          type="button"
          onClick={() => onDelete(campaign.id)}
          className="rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs text-red-700 hover:bg-red-100"
        >
          Delete
        </button>
      </div>
    </div>
  )
}
