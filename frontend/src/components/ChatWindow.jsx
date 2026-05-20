import { useEffect, useRef, useState } from 'react'

export default function ChatWindow({ messages, onSend, loading }) {
  const [input, setInput] = useState('')
  const [waitSec, setWaitSec] = useState(0)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => {
    if (!loading) {
      setWaitSec(0)
      return
    }
    const t0 = Date.now()
    const id = setInterval(() => setWaitSec(Math.floor((Date.now() - t0) / 1000)), 1000)
    return () => clearInterval(id)
  }, [loading])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    onSend(input.trim())
    setInput('')
  }

  const handleChoice = (choice) => {
    if (loading) return
    onSend(choice.value)
  }

  return (
    <div className="flex h-[calc(100vh-12rem)] flex-col rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="space-y-2 text-center text-sm text-slate-500">
            <p>
              If your prompt is missing details (dataset, send vs draft, campaign type), the agent will
              show <strong className="text-slate-700">clickable choices</strong> before running tools.
            </p>
            <p>
              Example: &quot;Create a birthday campaign&quot; → pick dataset → pick draft or send → agent builds the campaign.
            </p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-[90%] rounded-lg px-4 py-3 text-sm ${
              msg.role === 'user'
                ? 'ml-auto bg-indigo-600 text-white'
                : 'border border-slate-200 bg-slate-50 text-slate-800'
            }`}
          >
            <p className="mb-1 text-xs font-medium opacity-70">
              {msg.role === 'user' ? 'You' : 'Agent'}
            </p>
            <p className="whitespace-pre-wrap">{msg.content}</p>
            {msg.role === 'agent' && msg.clarification?.choices?.length > 0 && (
              <div className="mt-3 space-y-2 border-t border-slate-200 pt-3">
                <p className="text-xs text-slate-500">Choose one:</p>
                <div className="flex flex-col gap-2">
                  {msg.clarification.choices.map((choice) => (
                    <button
                      key={choice.id}
                      type="button"
                      disabled={loading}
                      onClick={() => handleChoice(choice)}
                      className="rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-2 text-left text-sm text-indigo-800 transition hover:border-indigo-300 hover:bg-indigo-100 disabled:opacity-50"
                    >
                      {choice.label}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="rounded-lg border border-indigo-100 bg-indigo-50 px-4 py-3 text-sm text-indigo-900">
            <p className="font-medium text-indigo-700">Working… ({waitSec}s)</p>
            <p className="mt-1 text-xs text-indigo-600">
              The model may call several tools (subject, body, save). This often takes 30s–2min — request is still running.
            </p>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2 border-t border-slate-200 p-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe your email campaign..."
          className="flex-1 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm text-slate-800 placeholder:text-slate-400"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  )
}

