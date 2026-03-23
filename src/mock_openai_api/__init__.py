import time
import uuid

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Mock OpenAI API",
    description="A mock OpenAI-compatible API that reminds you to use a real LLM endpoint.",
    version="1.0.0",
)

MOCK_MODEL_ID = "mock-llm-v1"

MOCK_RESPONSE = (
    "Hi there! You're talking to a **mock API**, not a real language model. "
    "This service exists for DevOps testing and exam purposes only. "
    "To get real AI responses, point your OpenWebUI instance to an actual LLM API "
    "(e.g., OpenAI, Anthropic, or a SageMaker endpoint). "
    "Check your OPENAI_API_BASE_URL environment variable!"
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": MOCK_MODEL_ID,
                "object": "model",
                "created": 1700000000,
                "owned_by": "devops-exam",
            }
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    model = body.get("model", MOCK_MODEL_ID)

    return JSONResponse(
        content={
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": MOCK_RESPONSE,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 50,
                "total_tokens": 60,
            },
        }
    )


def main():
    uvicorn.run(
        "mock_openai_api:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()
