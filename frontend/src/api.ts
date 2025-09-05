import type { ChatRequest, ChatResponse, UsageSummaryItem } from './types'

export async function sendChat(req: ChatRequest): Promise<ChatResponse> {
  const r = await fetch('http://localhost:8000/api/llm/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export async function fetchSummary(): Promise<UsageSummaryItem[]> {
  const r = await fetch('http://localhost:8000/api/usage/summary')
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
