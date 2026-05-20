import { useCallback, useEffect, useState } from 'react'
import ContactTable from '../components/ContactTable'
import DatasetUploadBox from '../components/DatasetUploadBox'
import { deleteDataset, getContacts, getDatasets, uploadDataset } from '../services/api'

export default function Datasets() {
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalContacts, setModalContacts] = useState(null)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    getDatasets()
      .then((res) => setDatasets(res.data))
      .catch(() => setError('Failed to load datasets'))
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleUpload = async (formData) => {
    setLoading(true)
    setError('')
    try {
      await uploadDataset(formData)
      load()
    } catch (e) {
      setError(e.response?.data?.detail || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const viewContacts = async (id) => {
    const res = await getContacts(id)
    setModalContacts(res.data)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this dataset and all contacts?')) return
    await deleteDataset(id)
    load()
  }

  return (
    <div>
      <h2 className="mb-6 text-2xl font-bold text-slate-800">Datasets</h2>
      {error && <p className="mb-4 text-sm text-red-600">{error}</p>}
      <DatasetUploadBox onUpload={handleUpload} loading={loading} />

      <div className="mt-8 overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-slate-100 text-left text-slate-700">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">File</th>
              <th className="px-4 py-3">Contacts</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map((d) => (
              <tr key={d.id} className="border-t border-slate-200">
                <td className="px-4 py-3 text-slate-800">{d.name}</td>
                <td className="px-4 py-3 text-slate-500">{d.file_name}</td>
                <td className="px-4 py-3">{d.contact_count}</td>
                <td className="px-4 py-3 space-x-2">
                  <button
                    type="button"
                    onClick={() => viewContacts(d.id)}
                    className="text-indigo-600 hover:underline"
                  >
                    View
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(d.id)}
                    className="text-red-600 hover:underline"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modalContacts && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-400/40 p-4">
          <div className="max-h-[80vh] w-full max-w-2xl overflow-auto rounded-xl border border-slate-200 bg-white p-6 shadow-xl">
            <div className="mb-4 flex justify-between">
              <h3 className="font-semibold text-slate-800">Contacts</h3>
              <button type="button" onClick={() => setModalContacts(null)} className="text-slate-500 hover:text-slate-700">
                Close
              </button>
            </div>
            <ContactTable contacts={modalContacts} />
          </div>
        </div>
      )}
    </div>
  )
}

