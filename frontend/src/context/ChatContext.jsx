import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { getChatHistory, sendChat } from '../services/api'

const ChatContext = createContext(null)

export function ChatProvider({ children }) {
  const [messages, setMessages] = useState([])
  const [historyLoaded, setHistoryLoaded] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    getChatHistory()
      .then((res) => {
        if (cancelled) return
        const history = []
        res.data.forEach((item) => {
          history.push({ role: 'user', content: item.prompt })
          history.push({
            role: 'agent',
            content: item.response,
            clarification: item.clarification || null,
          })
        })
        setMessages(history)
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setHistoryLoaded(true)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const sendMessage = useCallback(async (prompt, options = {}) => {
    setMessages((prev) => [...prev, { role: 'user', content: prompt }])
    setLoading(true)
    setError('')
    try {
      const res = await sendChat(prompt, options)
      setMessages((prev) => [
        ...prev,
        {
          role: 'agent',
          content: res.data.response,
          clarification: res.data.clarification || null,
        },
      ])
    } catch (e) {
      const detail = e.response?.data?.detail
      const isTimeout =
        e.code === 'ECONNABORTED' ||
        (typeof e.message === 'string' && e.message.toLowerCase().includes('timeout'))
      const msg = isTimeout
        ? 'Request timed out after 4 minutes. Try again with a shorter prompt or check the backend.'
        : typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
            ? detail.map((d) => d.msg || d).join(' ')
            : 'Agent request failed. Check OpenRouter API key and backend logs.'
      setError(msg)
      setMessages((prev) => [...prev, { role: 'agent', content: `Error: ${msg}` }])
    } finally {
      setLoading(false)
    }
  }, [])

  const value = useMemo(
    () => ({
      messages,
      loading,
      error,
      historyLoaded,
      sendMessage,
    }),
    [messages, loading, error, historyLoaded, sendMessage],
  )

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
}

export function useChat() {
  const ctx = useContext(ChatContext)
  if (!ctx) {
    throw new Error('useChat must be used within ChatProvider')
  }
  return ctx
}
