
from flask import Flask
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = '7192034833:AAHdW7xJBwzMgz8FJ6pPb11fGCDyzHmsasA'
CHANNEL_USERNAME = '@freeinstagramfollowers_10'
ADMIN_ID = 6178260867

app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

user_data = {}

def send_main_menu(context, chat_id, name, lang):
    buttons = [
        [InlineKeyboardButton("🌐 Website", url="https://free-insta-followers.netlify.app/")],
        [InlineKeyboardButton("🆓 Get Free Followers", callback_data="get_followers")]
    ]

    if lang == "en":
        text = f"👋 Hello {name}!\n\n🎉 *Welcome to Team Tasmina's Insta Followers Bot!*\n\n🚀 Get real followers for FREE!\nChoose an option below 👇"
    else:
        text = f"🥳 Hello {name}!\n\n🔥 *Team Tasmina ke Insta Followers Bot mein dil se swagat hai!*\n\n💥 Ab free mein real followers milenge bhai! 👇 Option chuno aur chalu ho jao!"

    context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    name = update.effective_user.full_name
    username = update.effective_user.username or "NoUsername"

    # DM to admin
    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"⚡ *New user started the bot!*\n👤 *Name:* {name}\n🆔 *ID:* `{user_id}`\n🔗 *Username:* @{username}",
        parse_mode="Markdown"
    )

    # Ask for language
    buttons = [
        [
            InlineKeyboardButton("🇮🇳 Hinglish", callback_data="lang_hinglish"),
            InlineKeyboardButton("🇺🇸 English", callback_data="lang_english")
        ]
    ]
    context.bot.send_message(
        chat_id=user_id,
        text="🌐 Please choose your language:\n🌐 कृपया अपनी भाषा चुनें:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def language_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    name = query.from_user.first_name
    query.answer()

    lang = "en" if "english" in query.data else "hi"
    user_data[user_id] = {"lang": lang}

    chat = context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    if chat.status in ["member", "administrator", "creator"]:
        send_main_menu(context, user_id, name, lang)
    else:
        join_text = (
            f"⚠️ *Hello {name},*\n\nPlease join our channel to continue using the bot.\nAfter joining, click '✅ I Have Joined'."
            if lang == "en"
            else f"🚫 Oye {name}! Pehle channel join karo tabhi aage badh paoge 👇\n\nJoin karne ke baad '✅ I Have Joined' dabao bhai 🙏"
        )
        buttons = [
            [InlineKeyboardButton("🔗 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ I Have Joined", callback_data="check_join")]
        ]
        query.message.reply_text(join_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

def check_join(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    name = query.from_user.first_name
    lang = user_data.get(user_id, {}).get("lang", "en")

    chat = context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    if chat.status in ["member", "administrator", "creator"]:
        query.message.reply_text("✅ Verified! 🎉", parse_mode="Markdown")
        send_main_menu(context, user_id, name, lang)
    else:
        retry = (
            f"❌ You're still not a member, {name}. Please join first."
            if lang == "en"
            else f"😓 {name}, abhi bhi channel join nahi kiya hai! Pehle usko join karo fir aana 🫣"
        )
        query.message.reply_text(retry)

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    lang = user_data.get(user_id, {}).get("lang", "en")
    user_data[user_id]["step"] = "ask_username"

    ask = "📱 Enter your Instagram username:" if lang == "en" else "👀 Jaldi se apna Insta username bhejo bhai! 💬"
    context.bot.send_message(chat_id=user_id, text=ask)

def handle_messages(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    full_name = update.effective_user.full_name
    message = update.message.text
    lang = user_data.get(user_id, {}).get("lang", "en")

    if user_id not in user_data:
        return

    state = user_data[user_id]

    if state.get("step") == "ask_username":
        state["username"] = message
        state["step"] = "ask_followers"
        text = "🔢 How many followers do you want? (e.g., 50, 100)" if lang == "en" else "🤔 Kitne followers chahiye? (jaise 50, 100) ✨"
        update.message.reply_text(text)

    elif state.get("step") == "ask_followers":
        if message.isdigit():
            state["followers"] = int(message)

            if lang == "en":
                text = (
                    f"✅ *Thank you {name}!* 🎉\n\n"
                    f"📝 Your request for *{state['followers']}* followers has been submitted.\n"
                    "⏳ Please wait up to *24 hours*.\n\n"
                    "🤝 DM us if needed: [@Lasmini_haobam__](https://instagram.com/Lasmini_haobam__)\n\n"
                    "❤️ Stay tuned for more giveaways!\n#TeamTasmina 🔥"
                )
            else:
                text = (
                    f"✅ *Shukriya {name}!* ❤️\n\n"
                    f"📤 Tumhara request *{state['followers']}* followers ke liye bhej diya gaya hai!\n"
                    "🕒 24 ghante tak ka wait karo bhai 😇\n\n"
                    "📩 Agar nahi aaye toh DM karo: [@Lasmini_haobam__](https://instagram.com/Lasmini_haobam__)\n\n"
                    "🔥 Aur tricks aur giveaways ke liye bane raho! #TeamTasmina"
                )

            update.message.reply_text(text, parse_mode="Markdown")

            context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "📥 New Follower Request:\n\n"
                    f"👤 Name: {full_name} (ID: `{user_id}`)\n"
                    f"📸 Username: `{state['username']}`\n"
                    f"🔢 Followers Wanted: {state['followers']}"
                ),
                parse_mode="Markdown"
            )

            del user_data[user_id]
        else:
            msg = "❌ Please enter a valid number (e.g., 50, 100)." if lang == "en" else "❗ Bhai number galat hai! Sahi number bhejo jaise 50, 100 😅"
            update.message.reply_text(msg)

def main():
    keep_alive()
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(language_selected, pattern="lang_"))
    dp.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
    dp.add_handler(CallbackQueryHandler(button_callback, pattern="get_followers"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_messages))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
