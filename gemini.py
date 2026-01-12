import requests
import json

API_KEY = "AIzaSyALiPylEzsSBb5Vzi_BtYjowPWX7Pzqn9M"

url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY
}

print("🤖 Gemini AI ready (Python 3.13 compatible)\n")

while True:
    text = input("You: ")
    if text.lower() == "exit":
        break

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": text}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    if "candidates" in data:
        print("Gemini:", data["candidates"][0]["content"]["parts"][0]["text"])
    else:
        print("ERROR RESPONSE:\n", json.dumps(data, indent=2))