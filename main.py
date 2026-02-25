import os
import time
import requests
from pyrogram import Client

# ================= कॉन्फ़िगरेशन =================
API_ID = int(os.environ.get("API_ID", "123456")) 
API_HASH = os.environ.get("API_HASH", "आपका_hash") 
SESSION_STRING = os.environ.get("SESSION_STRING", "आपका_string_session") 
CHAT_ID = int(os.environ.get("CHAT_ID", "-100xxxxxxxxxx")) 
LOG_CHAT = os.environ.get("LOG_CHAT", "me") 
# ===============================================

app = Client("my_account", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

def download_file(url, file_name):
    print(f"📥 Downloading: {file_name}...")
    url = url.replace(" ", "%20") 
    
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("✅ Downloaded Successfully!")
    return file_name

def process_links():
    with open("data.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    with app:
        app.send_message(LOG_CHAT, "🚀 **Script Started:** Downloading and Uploading process has begun!")

        # ====== नया जादुई कोड (Channel Cache करने के लिए) ======
        print("🔄 Pyrogram की मेमोरी रिफ्रेश हो रही है...")
        try:
            # यह आपके टेलीग्राम के रीसेंट चैट्स चेक करेगा ताकि चैनल की ID उसे मिल जाए
            for dialog in app.get_dialogs(limit=100):
                if dialog.chat.id == CHAT_ID:
                    print("✅ Channel Cache Success! अब कोई एरर नहीं आएगा।")
                    break
        except Exception as e:
            print(f"⚠️ Cache warning: {e}")
        # =========================================================

        for line in lines:
            line = line.strip()
            if not line or " : " not in line:
                continue
            
            parts = line.split(" : ")
            title = parts[0].strip()
            url = parts[1].strip()
            
            ext = ".mp4" if ".mp4" in url else ".pdf"
            safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c in (' ', '-', '_', '|', '(', ')', '.')]).rstrip()
            file_name = f"{safe_title}{ext}"
            
            caption = f"📚 **{title}**\n━━━━━━━━━━━━━━━━━\n🌟 **Extracted by @cryvex4**"
            
            # डाउनलोड 
            try:
                download_file(url, file_name)
            except Exception as e:
                print(f"❌ Error downloading {file_name}: {e}")
                app.send_message(LOG_CHAT, f"❌ **Download Failed:**\n📁 {title}\n⚠️ Error: `{e}`")
                continue
            
            # अपलोड
            print(f"📤 Uploading to Telegram: {file_name}...")
            try:
                if ext == ".mp4":
                    app.send_video(chat_id=CHAT_ID, video=file_name, caption=caption, supports_streaming=True)
                else:
                    app.send_document(chat_id=CHAT_ID, document=file_name, caption=caption)
                
                print("✅ Uploaded Successfully!")
                app.send_message(LOG_CHAT, f"✅ **Upload Success:**\n📁 `{title}` has been uploaded.")
                
            except Exception as e:
                print(f"❌ Upload Failed: {e}")
                app.send_message(LOG_CHAT, f"❌ **Upload Failed:**\n📁 `{title}`\n⚠️ Error: `{e}`")
            
            # फाइल डिलीट
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"🗑️ Deleted local file: {file_name}\n")
            
            time.sleep(10) 
        
        app.send_message(LOG_CHAT, "🎉 **All Tasks Completed!**")

if __name__ == "__main__":
    process_links()
