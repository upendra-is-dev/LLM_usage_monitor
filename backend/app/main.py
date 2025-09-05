import os
import httpx
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import UsageLog
from .schemas import ChatRequest, ChatResponse, UsageSummaryItem

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

app = FastAPI(title="LLM Usage Monitoring Service")

# Allow any origin during assessment; nginx handles same-origin in container
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

@app.post("/api/llm/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    url = f"{OPENAI_API_BASE}/chat/completions"
    payload = {
        "model": req.model,
        "messages": [
            {"role": "user", "content": req.prompt},
        ],
    }
    headers = {"Authorization": f"Bearer {req.api_key}"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            msg = e.response.text
            raise HTTPException(status_code=e.response.status_code, detail=msg)
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=str(e))

    data = r.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:  # pragma: no cover - defensive
        raise HTTPException(status_code=502, detail="Malformed OpenAI response")

    usage = data.get("usage", {})
    in_tok = int(usage.get("prompt_tokens", 0))
    out_tok = int(usage.get("completion_tokens", 0))

    db.add(UsageLog(user_label=req.user_label, model=req.model, input_tokens=in_tok, output_tokens=out_tok))
    db.commit()

    return ChatResponse(content=content)

@app.get("/api/usage/summary", response_model=list[UsageSummaryItem])
def usage_summary(db: Session = Depends(get_db)):
    stmt = (
        select(
            UsageLog.model,
            UsageLog.user_label,
            func.coalesce(func.sum(UsageLog.input_tokens), 0).label("total_input_tokens"),
            func.coalesce(func.sum(UsageLog.output_tokens), 0).label("total_output_tokens"),
        )
        .group_by(UsageLog.model, UsageLog.user_label)
        .order_by(UsageLog.model, UsageLog.user_label)
    )
    rows = db.execute(stmt).all()
    return [
        UsageSummaryItem(
            model=row.model,
            user_label=row.user_label,
            total_input_tokens=int(row.total_input_tokens or 0),
            total_output_tokens=int(row.total_output_tokens or 0),
        )
        for row in rows
    ]