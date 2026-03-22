import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import io
import os


class PuruliaVision:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"👁️ Initializing Vision Engine on {self.device}...")

        self.classes = ['purulia_culture', 'purulia_hills', 'purulia_nature', 'purulia_temple']

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        self.model = models.resnet18(weights=None)
        self.model.fc = nn.Linear(self.model.fc.in_features, len(self.classes))

        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "save", "resnet18_model.pth")

        try:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model = self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            print("✅ Vision Model Loaded Successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Vision model not found at {model_path}. Error: {e}")
            self.is_loaded = False

    def predict_image(self, image_bytes, threshold=0.60):
        """
        threshold: The confidence percentage required to accept the prediction.
        0.75 means the model must be 75% sure, otherwise it returns 'unknown'.
        """
        if not self.is_loaded:
            return {"error": "Vision model not loaded.", "predicted_class": None}

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(image_tensor)

                # Convert raw scores to probabilities (percentages)
                probabilities = F.softmax(outputs, dim=1)

                # Get the highest probability and its class index
                max_prob, predicted = torch.max(probabilities, 1)

            confidence = max_prob.item()
            predicted_class = self.classes[predicted.item()]

            # Check if the model is confident enough
            if confidence < threshold:
                return {
                    "predicted_class": "unknown",
                    "confidence": confidence,
                    "status": "success"
                }

            return {
                "predicted_class": predicted_class,
                "confidence": confidence,
                "status": "success"
            }

        except Exception as e:
            return {"error": str(e), "predicted_class": None, "status": "failed"}