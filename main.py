import os
import time
import requests
from pyrogram import Client

# ================= कॉन्फ़िगरेशन =================
API_ID = int(os.environ.get("API_ID", "1234567")) # अपनी API ID डालें 
API_HASH = os.environ.get("API_HASH", "अपना_API_HASH_यहाँ_डालें")

# Bot Token (अगर फाइल्स 50MB से छोटी हैं)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "अपना_BOT_TOKEN_यहाँ_डालें") 

# String Session (अगर फाइल्स 50MB से बड़ी हैं, तो इसे यूज़ करें। Bot Token खाली छोड़ दें)
SESSION_STRING = os.environ.get("SESSION_STRING", "") 

CHAT_ID = int(os.environ.get("CHAT_ID", "-100xxxxxxxxxx")) # अपनी Private Channel ID डालें
# ===============================================

# Pyrogram Client Setup
if SESSION_STRING:
    app = Client("my_account", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
else:
    app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def download_file(url, file_name):
    print(f"📥 Downloading: {file_name}...")
    url = url.replace(" ", "%20") # URL के स्पेस को फिक्स करने के लिए
    
    # Chunked Download (ताकि RAM फुल न हो)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("✅ Downloaded Successfully!")
    return file_name

def process_links():
    # data.txt से लिंक्स पढ़ना
    with open("data.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    with app:
        for line in lines:
            line = line.strip()
            if not line or " : " not in line:
                continue
            
            # Title और URL को अलग करना
            parts = line.split(" : ")
            title = parts[0].strip()
            url = parts[1].strip()
            
            # फाइल का नाम और एक्सटेंशन बनाना
            ext = ".mp4" if ".mp4" in url else ".pdf"
            # फाइल का नाम क्लीन करना ताकि सेव करने में एरर न आए
            safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c in (' ', '-', '_', '|', '(', ')', '.')]).rstrip()
            file_name = f"{safe_title}{ext}"
            
            # प्रोफेशनल कैप्शन तैयार करना
            caption = f"📚 **{title}**\n━━━━━━━━━━━━━━━━━\n🌟 **Extracted by @cryvex4**"
            
            # 1. डाउनलोड करें
            download_file(url, file_name)
            
            # 2. अपलोड करें
            print(f"📤 Uploading to Telegram: {file_name}...")
            try:
                if ext == ".mp4":
                    app.send_video(chat_id=CHAT_ID, video=file_name, caption=caption, supports_streaming=True)
                else:
                    app.send_document(chat_id=CHAT_ID, document=file_name, caption=caption)
                print("✅ Uploaded Successfully!")
            except Exception as e:
                print(f"❌ Upload Failed: {e}")
            
            # 3. तुरंत डिलीट करें (स्टोरेज बचाने के लिए)
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"🗑️ Deleted local file: {file_name}\n")
            
            # अगली फाइल डाउनलोड करने से पहले 5 सेकंड रुकें (ताकि Telegram ब्लॉक न करे)
            time.sleep(5) 

if __name__ == "__main__":
    print("🚀 Script Started...")
    process_links()
    print("🎉 All tasks completed!")
