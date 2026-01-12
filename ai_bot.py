import subprocess, time, json, threading, requests
from PIL import Image
import google.generativeai as genai
import tkinter as tk
import traceback

GEN_API_KEY = "AIzaSyALiPylEzsSBb5Vzi_BtYjowPWX7Pzqn9M"
SERVER_URL = "http://192.168.1.7:8000"  # Change if LAN IP

genai.configure(api_key=GEN_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

running = True
start_time = time.time()
MAX_RUNTIME = 300  # 5 minutes
CHECK_INTERVAL = 2

PROMPT = """
You are playing an Android game.
If PLAY or START button visible → tap it.
If reward or collect button → tap.
If OK button → tap.
If redirect to a website → tap back button.
If gun's notch on bottle → tap attack.
when gun's notch on bottle → tap attack.
Respond only JSON:
{"tap":[x,y]} OR {"wait":true}
"""

def stop_bot():
    global running
    running = False
    print("🛑 BOT STOPPED")

def send_error_to_server(error_text):
    try:
        requests.post(f"{SERVER_URL}/error", json={"error": error_text}, timeout=2)
    except:
        print("❌ Could not send error to server")

def stop_ui():
    root = tk.Tk()
    root.title("STOP AI BOT")
    root.geometry("200x100")
    tk.Button(root, text="STOP BOT", bg="red", fg="white",
              command=stop_bot).pack(expand=True, fill="both")
    root.mainloop()

def server_alive():
    try:
        r = requests.get(f"{SERVER_URL}/ping", timeout=2)
        return r.status_code == 200
    except:
        return False

def adb_screenshot():
    subprocess.run("adb exec-out screencap -p > screen.png", shell=True)
    return Image.open("screen.png")

def adb_tap(x, y):
    subprocess.run(f"adb shell input tap {x} {y}", shell=True)

def ai_decide(img):
    try:
        res = model.generate_content([PROMPT, img])
        return json.loads(res.text)
    except Exception as e:
        raise Exception(f"AI Decision Error: {str(e)}")

def bot_loop():
    global running
    while running:
        try:
            # ⏱ Time limit
            if time.time() - start_time > MAX_RUNTIME:
                print("⏱ Time limit reached")
                stop_bot()
                break

            # 🛑 Server check
            if not server_alive():
                print("❌ Server offline")
                stop_bot()
                break

            img = adb_screenshot()
            decision = ai_decide(img)

            if "tap" in decision:
                x, y = decision["tap"]
                adb_tap(x, y)

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            error_text = traceback.format_exc()
            print(error_text)
            send_error_to_server(error_text)
            stop_bot()
            break

threading.Thread(target=stop_ui, daemon=True).start()
bot_loop()