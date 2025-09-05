from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(..., description="OpenAI model name, e.g. gpt-5-mini")
    user_label: str
    prompt: str

class ChatResponse(BaseModel):
    content: str

class UsageSummaryItem(BaseModel):
    model: str
    user_label: str
    total_input_tokens: int
    total_output_tokens: int