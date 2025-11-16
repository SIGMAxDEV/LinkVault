# ================================================
# 🔐 LINKVAULT X BOT — ULTRA STORAGE EDITION
# 👨‍💻 Developer: @SigmaDoxx
# 🛰 100% Telegram-Based Cloud Storage
# 📦 No server, No DB, No Mongo, No hosting files
# ================================================

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random, string
import json, os   # ← ADDED

# ------------------------------------------------
# 🔧 CONFIG — CHANGE THESE
# ------------------------------------------------

BOT_TOKEN = "8212674733:AAGbldHSNzt5lTYIRdzZj-ZvQdkqs1gE_GY"
ADMIN_ID = 6193742824
STORAGE_CHANNEL = -1003303374370 
FORCE_JOIN_CHANNEL = "@SigmaDox0"

bot = telebot.TeleBot(BOT_TOKEN)

# Temporary RAM memory storage
fileDB = {}

# ====== LOAD OLD DB IF EXISTS ======
if os.path.exists("fileDB.json"):
    with open("fileDB.json", "r") as f:
        fileDB = json.load(f)
# ===================================


# ------------------------------------------------
# 🔑 Unique Key Generator
# ------------------------------------------------
def gen_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# ------------------------------------------------
# 🔍 Check User Joined Channel
# ------------------------------------------------
def is_member(user_id):
    try:
        st = bot.get_chat_member(FORCE_JOIN_CHANNEL, user_id).status
        return st in ["member", "administrator", "creator"]
    except:
        return False

# ------------------------------------------------
# 🏁 START COMMAND
# ------------------------------------------------
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id

    # For key-based file retrieval
    args = msg.text.split()
    if len(args) > 1:
        key = args[1]
        if key in fileDB:
            serve_file(msg.chat.id, key)
            return
        else:
            bot.send_message(msg.chat.id, "❌ Invalid or expired link.")
            return

    # Force Join Logic
    if not is_member(uid):
        join_btn = InlineKeyboardMarkup()
        join_btn.add(
            InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_JOIN_CHANNEL.replace('@','')}")
        )
        bot.send_message(
            msg.chat.id,
            "🔒 **Access Locked!**\n\n"
            "Please join our channel to use this bot:",
            reply_markup=join_btn,
            parse_mode="Markdown"
        )
        return
    
    # Video Welcome (Optional)
    # Normal Welcome
    VIDEO_ID = "https://t.me/PIROxSIGMA/176"
    bot.send_video(
    msg.chat.id,
    VIDEO_ID,
    caption=(
        "🎉 *Welcome to LinkVault X Bot!*\n\n"
        "Securely store your:\n"
        "📁 Documents\n🖼 Photos\n🎞 Videos\n🎧 Audios\n📝 Stickers & GIFs\n\n"
        "Just send me *any file* & I’ll generate a private download link.\n\n"
        "🔐 Your privacy, our priority.\n"
        "👨‍💻 Developed by: @SigmaDoxx"
    ),
    parse_mode="Markdown",
    supports_streaming=True
)
# ------------------------------------------------
# 📥 FILE RECEIVE HANDLER (ALL MEDIA TYPES)
# ------------------------------------------------
@bot.message_handler(content_types=[
    'document','photo','video','audio','voice','sticker','animation'
])
def file_handler(msg):
    uid = msg.from_user.id

    # Force Join Logic
    if not is_member(uid):
        bot.send_message(msg.chat.id, "❌ Please join the channel first. @SigmaDox0")
        return

    # Forward file to private storage channel
    stored = bot.forward_message(STORAGE_CHANNEL, msg.chat.id, msg.message_id)

    # Extract metadata
    ftype, fname, fsize = get_file_info(msg)

    # Generate file key
    key = gen_key()

    # Save file reference
    fileDB[key] = {
        "msg_id": stored.message_id,
        "name": fname,
        "size": fsize,
        "type": ftype
    }

    # ====== SAVE TO JSON ======
    with open("fileDB.json", "w") as f:
        json.dump(fileDB, f)
    # ==========================

    # Magic link
    link = f"https://t.me/{bot.get_me().username}?start={key}"

    # Send reply to user
    bot.send_message(
        msg.chat.id,
        f"📦 **File Saved Successfully!**\n\n"
        f"🔹 **Name:** `{fname}`\n"
        f"🔹 **Type:** `{ftype}`\n"
        f"🔹 **Size:** `{fsize}`\n\n"
        f"🔗 **Private Link:**\n{link}\n\n"
        f"🔒 Only people with the link can download.\n"
        f"💡 Share it safely.\n\n"
        f"👨‍💻 By @SigmaDoxx",
        parse_mode="Markdown"
    )

# ------------------------------------------------
# 📤 SERVE FILE BACK TO USER
# ------------------------------------------------
def serve_file(chat_id, key):
    data = fileDB[key]

    # Copy file back from storage
    bot.copy_message(
        chat_id,
        STORAGE_CHANNEL,
        data["msg_id"]
    )

    bot.send_message(
        chat_id,
        f"📥 **File Retrieved Successfully!**\n\n"
        f"📌 **Name:** `{data['name']}`\n"
        f"📌 **Type:** `{data['type']}`\n"
        f"📌 **Size:** `{data['size']}`\n\n"
        f"🔐 Delivered securely via LinkFileXBot.\n"
        f"Powered by @SigmaDoxx",
        parse_mode="Markdown"
    )

# ------------------------------------------------
# 🧠 FILE INFO PARSER
# ------------------------------------------------
def get_file_info(msg):
    if msg.document:
        return ("Document", msg.document.file_name, f"{round(msg.document.file_size/1024,2)} KB")

    if msg.photo:
        p = msg.photo[-1]
        return ("Photo", "Image.jpg", f"{round(p.file_size/1024,2)} KB")

    if msg.video:
        return ("Video", msg.video.file_name or "Video.mp4", f"{round(msg.video.file_size/1024,2)} KB")

    if msg.audio:
        return ("Audio", msg.audio.file_name or "Audio.mp3", f"{round(msg.audio.file_size/1024,2)} KB")

    if msg.voice:
        return ("Voice Note", "Voice.ogg", f"{round(msg.voice.file_size/1024,2)} KB")

    if msg.sticker:
        return ("Sticker", "Sticker.webp", "N/A")

    if msg.animation:
        return ("GIF", "Animation.gif", f"{round(msg.animation.file_size/1024,2)} KB")

    return ("Unknown", "Unknown", "0 KB")

# ------------------------------------------------
# 🚨 ADMIN COMMAND
# ------------------------------------------------
@bot.message_handler(commands=['stats'])
def stats(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    bot.send_message(msg.chat.id, f"📊 Total Files Stored: {len(fileDB)}")

# ------------------------------------------------
# 🚀 START POLLING
# ------------------------------------------------
print("🚀 LinkVault X Bot is absolutely fukking amazing...")
bot.infinity_polling()
