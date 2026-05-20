import ChatWindow from '../components/ChatWindow'
import { useChat } from '../context/ChatContext'

export default function Chat() {
  const { messages, loading, error, historyLoaded, sendMessage } = useChat()

  return (
    <div>
      <h2 className="mb-2 text-2xl font-bold text-slate-800">AI Chat</h2>
      <p className="mb-4 text-sm text-slate-600">
        Missing dataset, send vs draft, or campaign type? You will get <strong className="text-slate-800">choice buttons</strong> before the agent runs (fast). You can switch pages while the agent works.
      </p>
      {!historyLoaded && (
        <p className="mb-2 text-sm text-slate-500">Loading chat history…</p>
      )}
      {error && <p className="mb-2 text-sm text-red-600">{error}</p>}
      <ChatWindow messages={messages} onSend={sendMessage} loading={loading} />
    </div>
  )
}
