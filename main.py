import os
import time
import requests
from pyrogram import Client

# ================= कॉन्फ़िगरेशन =================
# Railway Variables से डेटा लेना
API_ID = int(os.environ.get("API_ID", "123456")) # अपनी API ID
API_HASH = os.environ.get("API_HASH", "आपका_hash") # अपना API HASH
SESSION_STRING = os.environ.get("SESSION_STRING", "आपका_string_session") 
CHAT_ID = int(os.environ.get("CHAT_ID", "-100xxxxxxxxxx")) # जहाँ अपलोड करना है (Private Channel ID)

# नोटिफिकेशन कहाँ चाहिए? 
# अगर Bot पर चाहिए तो अपने Bot का Username लिखें (जैसे "@MyStatusBot")
# अगर अपने खुद के Saved Messages में चाहिए तो "me" लिखें।
LOG_CHAT = os.environ.get("LOG_CHAT", "me") 
# ===============================================

# सिर्फ String Session के साथ Client सेटअप
app = Client("my_account", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

def download_file(url, file_name):
    print(f"📥 Downloading: {file_name}...")
    url = url.replace(" ", "%20") # URL के स्पेस को फिक्स करने के लिए
    
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
        # स्क्रिप्ट चालू होते ही एक मैसेज भेजेगा
        app.send_message(LOG_CHAT, "🚀 **Script Started:** Downloading and Uploading process has begun!")

        for line in lines:
            line = line.strip()
            if not line or " : " not in line:
                continue
            
            # Title और URL अलग करना
            parts = line.split(" : ")
            title = parts[0].strip()
            url = parts[1].strip()
            
            # फाइल का नाम और एक्सटेंशन
            ext = ".mp4" if ".mp4" in url else ".pdf"
            safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c in (' ', '-', '_', '|', '(', ')', '.')]).rstrip()
            file_name = f"{safe_title}{ext}"
            
            # कैप्शन (Caption)
            caption = f"📚 **{title}**\n━━━━━━━━━━━━━━━━━\n🌟 **Extracted by @cryvex4**"
            
            # 1. डाउनलोड
            try:
                download_file(url, file_name)
            except Exception as e:
                print(f"❌ Error downloading {file_name}: {e}")
                app.send_message(LOG_CHAT, f"❌ **Download Failed:**\n📁 {title}\n⚠️ Error: `{e}`")
                continue
            
            # 2. अपलोड
            print(f"📤 Uploading to Telegram: {file_name}...")
            try:
                if ext == ".mp4":
                    app.send_video(chat_id=CHAT_ID, video=file_name, caption=caption, supports_streaming=True)
                else:
                    app.send_document(chat_id=CHAT_ID, document=file_name, caption=caption)
                
                print("✅ Uploaded Successfully!")
                # सक्सेसफुल होने पर Bot को मैसेज भेजना
                app.send_message(LOG_CHAT, f"✅ **Upload Success:**\n📁 `{title}` has been uploaded to the channel.")
                
            except Exception as e:
                print(f"❌ Upload Failed: {e}")
                # फेल होने पर Bot को मैसेज भेजना
                app.send_message(LOG_CHAT, f"❌ **Upload Failed:**\n📁 `{title}`\n⚠️ Error: `{e}`")
            
            # 3. लोकल फाइल डिलीट करना
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"🗑️ Deleted local file: {file_name}\n")
            
            # Telegram ब्लॉक न करे इसलिए 5-10 सेकंड का गैप
            time.sleep(10) 
        
        # सब खत्म होने पर फाइनल मैसेज
        app.send_message(LOG_CHAT, "🎉 **All Tasks Completed!** All files have been processed.")

if __name__ == "__main__":
    process_links()
