import { useRef, useState } from 'react'

const SAMPLE_PATH = '/samples/startup_leads.csv'

const COLUMNS = [
  { name: 'email', required: true, description: 'Recipient email address (one per row)' },
  { name: 'name', required: false, description: 'Contact name; used for {{name}} in emails' },
  { name: 'company', required: false, description: 'Company name; used for {{company}} in emails' },
]

const SAMPLE_ROWS = [
  { name: 'Alice Johnson', email: 'alice@example.com', company: 'TechNova' },
  { name: 'Bob Smith', email: 'bob@example.com', company: 'Innovate Labs' },
]

export default function DatasetUploadBox({ onUpload, loading }) {
  const inputRef = useRef(null)
  const [name, setName] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [sampleLoading, setSampleLoading] = useState(false)

  const handleFile = (file) => {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    if (name.trim()) formData.append('name', name.trim())
    onUpload(formData)
  }

  const handleSampleUpload = async () => {
    setSampleLoading(true)
    try {
      const res = await fetch(SAMPLE_PATH)
      if (!res.ok) throw new Error('Sample file not found')
      const blob = await res.blob()
      const file = new File([blob], 'startup_leads.csv', { type: 'text/csv' })
      const formData = new FormData()
      formData.append('file', file)
      formData.append('name', 'startup_leads')
      onUpload(formData)
    } catch {
      alert('Could not load sample dataset. Use Download sample CSV instead.')
    } finally {
      setSampleLoading(false)
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div
        className={`rounded-xl border-2 border-dashed p-8 text-center transition ${
          dragOver ? 'border-indigo-400 bg-indigo-50' : 'border-slate-300 bg-white'
        }`}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          handleFile(e.dataTransfer.files[0])
        }}
      >
        <p className="mb-4 text-slate-700">Drag & drop a CSV file here</p>
        <input
          type="text"
          placeholder="Dataset name (optional)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mb-4 w-full max-w-xs rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800"
        />
        <div className="flex flex-wrap items-center justify-center gap-2">
          <button
            type="button"
            disabled={loading}
            onClick={() => inputRef.current?.click()}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {loading ? 'Uploading...' : 'Choose CSV'}
          </button>
          <button
            type="button"
            disabled={loading || sampleLoading}
            onClick={handleSampleUpload}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            {sampleLoading ? 'Loading sample...' : 'Upload sample dataset'}
          </button>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        <p className="mt-4 text-xs text-slate-500">Only .csv files. Column headers are case-insensitive.</p>
      </div>

      <div className="space-y-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-slate-800">Required CSV columns</h3>
          <div className="overflow-x-auto rounded-lg border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100 text-xs uppercase text-slate-600">
                <tr>
                  <th className="px-3 py-2">Column</th>
                  <th className="px-3 py-2">Required</th>
                  <th className="px-3 py-2">Description</th>
                </tr>
              </thead>
              <tbody className="bg-white">
                {COLUMNS.map((col) => (
                  <tr key={col.name} className="border-t border-slate-200">
                    <td className="px-3 py-2 font-mono text-indigo-700">{col.name}</td>
                    <td className="px-3 py-2">
                      {col.required ? (
                        <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700">Required</span>
                      ) : (
                        <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">Optional</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-slate-600">{col.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-slate-500">
            If <span className="font-mono text-slate-700">name</span> is missing, the first column is used as the name.
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-semibold text-slate-800">Sample dataset</h3>
            <a
              href={SAMPLE_PATH}
              download="startup_leads.csv"
              className="text-xs text-indigo-600 hover:underline"
            >
              Download startup_leads.csv
            </a>
          </div>
          <p className="mb-3 text-xs text-slate-500">
            Use this format for your own file, or click <strong className="text-slate-700">Upload sample dataset</strong>{' '}
            to add it to your account.
          </p>
          <div className="overflow-x-auto rounded-lg border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-100">
                <tr>
                  <th className="px-3 py-2 font-mono text-xs text-indigo-700">name</th>
                  <th className="px-3 py-2 font-mono text-xs text-indigo-700">email</th>
                  <th className="px-3 py-2 font-mono text-xs text-indigo-700">company</th>
                </tr>
              </thead>
              <tbody className="bg-white">
                {SAMPLE_ROWS.map((row, i) => (
                  <tr key={i} className="border-t border-slate-200 text-slate-700">
                    <td className="px-3 py-2">{row.name}</td>
                    <td className="px-3 py-2">{row.email}</td>
                    <td className="px-3 py-2">{row.company}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}


