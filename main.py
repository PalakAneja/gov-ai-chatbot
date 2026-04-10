from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
from groq import Groq

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (frontend connect ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load schemes
with open("schemes.json") as f:
    schemes = json.load(f)

# 🔐 API key from environment (SAFE WAY)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Message(BaseModel):
    text: str

@app.post("/chat")
def chat(msg: Message):
    user_text = msg.text

    # schemes ko text me convert
    scheme_info = ""
    for s in schemes:
        scheme_info += f"{s['name']} - {s['eligibility']}\n"

    prompt = f"""
You are a helpful Indian government assistant.

Available schemes:
{scheme_info}

User question: {user_text}

Answer simply in friendly tone.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You help users find government schemes."},
                {"role": "user", "content": prompt}
            ]
        )

        reply = response.choices[0].message.content

        return {"reply": reply}

    except Exception as e:
        return {"reply": f"Error: {str(e)}"}
        