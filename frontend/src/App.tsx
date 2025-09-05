import { useEffect, useMemo, useState } from 'react'
import { fetchSummary, sendChat } from './api'
import type { UsageSummaryItem } from './types'
import './App.css'

export default function App() {
  const [apiKey, setApiKey] = useState('')
  const [userLabel, setUserLabel] = useState('alice')
  const [model, setModel] = useState('gpt-5-mini')
  const [prompt, setPrompt] = useState('Say hello!')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState<UsageSummaryItem[]>([])
  const [error, setError] = useState('')

  async function loadSummary() {
    try {
      const data = await fetchSummary()
      setSummary(data)
    } catch (e: any) {
      setError(String(e))
    }
  }

  useEffect(() => { loadSummary() }, [])

  const totalByModel = useMemo(() => {
    const map = new Map<string, { inTok: number, outTok: number }>()
    for (const row of summary) {
      const cur = map.get(row.model) || { inTok: 0, outTok: 0 }
      cur.inTok += row.total_input_tokens
      cur.outTok += row.total_output_tokens
      map.set(row.model, cur)
    }
    return Array.from(map.entries())
  }, [summary])

  async function onSend(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await sendChat({ api_key: apiKey, model, user_label: userLabel, prompt })
      setAnswer(res.content)
      await loadSummary()
    } catch (e: any) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header>
        <h1>LLM Usage Monitoring</h1>
        <p className="subtitle">Track token usage across models and users</p>
      </header>

      {/* Form Section */}
      <div className="form-card">
        <h2 className="form-title">💬 Send a Prompt</h2>
        <form onSubmit={onSend} className="modern-form">
          <div className="form-grid">
            <label>
              OpenAI API Key
              <input
                type="password"
                value={apiKey}
                onChange={e => setApiKey(e.target.value)}
                required
              />
            </label>
            <label style={{marginTop: "15px"}}>
              User Label
              <input
                value={userLabel}
                onChange={e => setUserLabel(e.target.value)}
                required
              />
            </label>
          </div>
          <label >
            Model
            <select value={model} onChange={e => setModel(e.target.value)}>
              <option value="gpt-5-mini">gpt-5-mini</option>
              <option value="gpt-4o-mini">gpt-4o-mini</option>
              <option value="gpt-4o">gpt-4o</option>
            </select>
          </label>
          <label>
            Prompt
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              rows={4}
            />
          </label>
          <button disabled={loading} className="submit-btn">
            {loading ? 'Sending…' : 'Send Prompt'}
          </button>
        </form>

        {error && <p className="error">{error}</p>}

        {answer && (
          <div className="response-card">
            <strong>LLM Response:</strong>
            <pre>{answer}</pre>
          </div>
        )}
      </div>

      {/* Dashboard Section */}
      <div className="dashboard">
        {/* Usage Dashboard */}
        <div className="card">
          <div className="card-header">📊 Usage Dashboard</div>
          <div className="table-wrapper">
            <table className="modern-table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>User Label</th>
                  <th className="right">Input Tokens</th>
                  <th className="right">Output Tokens</th>
                </tr>
              </thead>
              <tbody>
                {summary.map((row, i) => (
                  <tr key={i}>
                    <td>{row.model}</td>
                    <td>{row.user_label}</td>
                    <td className="right">{row.total_input_tokens}</td>
                    <td className="right">{row.total_output_tokens}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Totals by Model */}
        <div className="card">
          <div className="card-header">📌 Totals by Model</div>
          <ul className="totals-list">
            {totalByModel.map(([m, t]) => (
              <li key={m}>
                <span className="model">{m}</span>
                <span className="tokens">{t.inTok} in / {t.outTok} out</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
