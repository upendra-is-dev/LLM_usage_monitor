export type UsageSummaryItem = {
  model: string
  user_label: string
  total_input_tokens: number
  total_output_tokens: number
}

export type ChatRequest = {
  api_key: string
  model: string
  user_label: string
  prompt: string
}

export type ChatResponse = {
  content: string
}
