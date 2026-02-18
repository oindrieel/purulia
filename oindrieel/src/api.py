from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from oindrieel.src.pipeline import PuruliaBrain
app = FastAPI(title="Purulia Tourism AI API")

print("⏳ Starting API... Loading Brain...")
brain = PuruliaBrain()
print("✅ Brain Loaded and Ready!")

class UserRequest(BaseModel):
    text: str
    user_id: str = "guest"
@app.post("/chat")
async def chat_endpoint(request: UserRequest):
    """
    Receives text from the frontend/backend, processes it via the Brain,
    and returns the structured JSON response.
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        response = brain.process_query(request.text)
        response["user_id"] = request.user_id

        return response
    except Exception as e:
        return {"error": str(e), "type": "error"}


@app.get("/")
def home():
    """Health check endpoint to ensure API is running."""
    return {"status": "Online", "msg": "Purulia AI Brain is active."}
