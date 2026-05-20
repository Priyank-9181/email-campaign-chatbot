export default function ContactTable({ contacts }) {
  if (!contacts?.length) {
    return <p className="text-sm text-slate-500">No contacts in this dataset.</p>
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="w-full text-sm">
        <thead className="bg-slate-100 text-left text-slate-700">
          <tr>
            <th className="px-4 py-2">Name</th>
            <th className="px-4 py-2">Email</th>
            <th className="px-4 py-2">Company</th>
          </tr>
        </thead>
        <tbody className="bg-white">
          {contacts.map((c) => (
            <tr key={c.id} className="border-t border-slate-200">
              <td className="px-4 py-2 text-slate-800">{c.name || '—'}</td>
              <td className="px-4 py-2 text-slate-800">{c.email}</td>
              <td className="px-4 py-2 text-slate-600">{c.company || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
