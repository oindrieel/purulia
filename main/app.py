import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(ROOT_DIR, 'oindrieel'))
sys.path.append(os.path.join(ROOT_DIR, 'shubham_2'))

from src.pipeline import PuruliaBrain
from cv_engine import PuruliaVision
from src.data_loader import TourismDataHandler

app = FastAPI(title="Purulia Tourism AI")

current_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

print("⏳ Booting up Multimodal Systems...")
brain = PuruliaBrain()
vision = PuruliaVision()
data_handler = TourismDataHandler()
print("✅ All Systems Go!")


class TextRequest(BaseModel):
    text: str


@app.get("/")
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat")
async def chat_endpoint(request: TextRequest):
    if not request.text: raise HTTPException(status_code=400, detail="Text cannot be empty")
    return brain.process_query(request.text)


@app.post("/api/multimodal")
async def multimodal_endpoint(image: UploadFile = File(None), text: str = Form(None)):
    response = {"ai_message": "", "places": [], "vision_class": None}

    if image and image.filename:
        img_bytes = await image.read()
        cv_result = vision.predict_image(img_bytes)

        if cv_result.get("status") == "success":
            det_class = cv_result["predicted_class"]

            # --- NEW: HANDLE UNKNOWN IMAGES ---
            if det_class == "unknown":
                confidence = round(cv_result.get("confidence", 0) * 100, 1)
                response["vision_class"] = "unknown"
                response[
                    "ai_message"] += f"Hmm, I am not quite sure what this is (only {confidence}% confident). It doesn't look like a registered Purulia Heritage site to me! Are you sure this is from Purulia?\n\n"
            else:
                response["vision_class"] = det_class
                response["ai_message"] += f"I see an image of {det_class.replace('purulia_', '')}. "

                detected_places = []
                for place in data_handler.get_all_locations():
                    if place.get("cv_class") == det_class:
                        response["places"].append(place["name"])
                        detected_places.append(place["name"])

                # Save to brain memory
                brain.context["last_places"] = detected_places

    if text:
        nlp_result = brain.process_query(text)
        response["ai_message"] += f" Regarding your message: {nlp_result.get('text', '')}"
        if "itinerary" in nlp_result:
            response["itinerary"] = nlp_result["itinerary"]
            response["ai_message"] = "Here is your requested trip plan."

    return response


if __name__ == '__main__':
    print(f"API running on http://localhost:8080/")
    uvicorn.run(app, host="0.0.0.0", port=8080)