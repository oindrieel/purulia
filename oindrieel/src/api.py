from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from oindrieel.src.pipeline import PuruliaBrain

# 1. Initialize the App
# We initialize the Brain OUTSIDE the endpoint so it loads the model only once at startup.
app = FastAPI(title="Purulia Tourism AI API")

print("⏳ Starting API... Loading Brain...")
brain = PuruliaBrain()
print("✅ Brain Loaded and Ready!")


# 2. Define the Request Format (What Shuvam sends you)
class UserRequest(BaseModel):
    text: str
    user_id: str = "guest"  # Optional, useful for future context tracking


# 3. Define the Endpoint
@app.post("/chat")
async def chat_endpoint(request: UserRequest):
    """
    Receives text from the frontend/backend, processes it via the Brain,
    and returns the structured JSON response.
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # Pass input to your pipeline
        response = brain.process_query(request.text)

        # Add metadata (optional)
        response["user_id"] = request.user_id

        return response
    except Exception as e:
        # Log the error internally here if needed
        return {"error": str(e), "type": "error"}


@app.get("/")
def home():
    """Health check endpoint to ensure API is running."""
    return {"status": "Online", "msg": "Purulia AI Brain is active."}

# Instructions for running:
# uvicorn src.api:app --reload