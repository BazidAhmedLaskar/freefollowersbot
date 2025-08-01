import os
import re
import logging
from datetime import datetime, timedelta
from threading import Lock, Thread
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from telegram.error import TelegramError
from telegram.utils.helpers import escape_markdown

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN', '7311381977:AAG5MTPuYe0ltJEolWlYn1ZjVWbUir0ngWs')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@freefollowers_28')
ADMIN_ID = int(os.getenv('ADMIN_ID', '6178260867'))

# Flask app for keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive!"

def run():
    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        logger.error(f"Flask server error: {e}")

def keep_alive():
    Thread(target=run).start()

# Thread-safe user data storage
user_data = {}
user_data_lock = Lock()

def update_user_data(user_id, data):
    with user_data_lock:
        user_data[user_id] = data

def get_user_data(user_id):
    with user_data_lock:
        return user_data.get(user_id)

def send_main_menu(update, first_name):
    buttons = [
        [InlineKeyboardButton("🌐 Website", url="https://free-insta-followers.netlify.app/")],
        [InlineKeyboardButton("🆓 Get Free Followers", callback_data="get_followers")]
    ]
    try:
        update.message.reply_text(
            f"👋 Welcome {first_name}! Please choose an option below:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except TelegramError as e:
        logger.error(f"Failed to send main menu to {first_name}: {e}")
        update.message.reply_text("⚠️ An error occurred. Please try again later.")

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    logger.info(f"User {user_id} started the bot")
    try:
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
    except TelegramError as e:
        logger.error(f"Telegram API error in start: {e}")
        update.message.reply_text("⚠️ An error occurred. Please try again later.")

def check_join(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    first_name = query.from_user.first_name
    query.answer()
    try:
        chat = context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if chat.status in ["member", "administrator", "creator"]:
            query.message.reply_text(f"✅ Verified {first_name}! Now choose an option:")
            send_main_menu(update.callback_query, first_name)
        else:
            query.message.reply_text(f"❌ You're still not a member, {first_name}. Please join first.")
    except TelegramError as e:
        logger.error(f"Telegram API error in check_join: {e}")
        query.message.reply_text("⚠️ An error occurred. Please try again later.")

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    if get_user_data(user_id):
        context.bot.send_message(chat_id=user_id, text="⚠️ Please complete your current request first.")
        return
    update_user_data(user_id, {"step": "ask_username"})
    try:
        context.bot.send_message(chat_id=user_id, text="📱 Enter your Instagram username:")
    except TelegramError as e:
        logger.error(f"Telegram API error in button_callback: {e}")
        query.message.reply_text("⚠️ An error occurred. Please try again later.")

def handle_messages(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    full_name = update.effective_user.full_name
    tg_id = user_id
    message = update.message.text
    logger.info(f"Message from user {user_id}: {message}")

    state = get_user_data(user_id)
    if not state:
        update.message.reply_text("ℹ️ Please use /start to begin.")
        return

    if state["step"] == "ask_username":
        if not re.match(r'^[A-Za-z0-9._]{1,30}$', message):
            update.message.reply_text("❌ Invalid Instagram username. Use letters, numbers, dots, or underscores (max 30 characters).")
            return
        state["username"] = message
        state["step"] = "ask_followers"
        update_user_data(user_id, state)
        update.message.reply_text("🔢 How many followers do you want? (50-500)")

    elif state["step"] == "ask_followers":
        last_request = state.get("last_request")
        if last_request and datetime.now() < last_request + timedelta(hours=24):
            update.message.reply_text("⏳ You can only request followers once every 24 hours.")
            return
        if not message.isdigit() or not (50 <= int(message) <= 500):
            update.message.reply_text("❌ Please enter a valid number between 50 and 500.")
            return
        state["followers"] = int(message)
        state["last_request"] = datetime.now()
        update_user_data(user_id, state)
        try:
            update.message.reply_text(
                f"✅ Thank you {first_name}!\n\n"
                f"Your request for *{state['followers']}* followers has been submitted successfully. Please wait up to *24 hours*.\n"
                "If you don't receive them, DM me on Instagram: [@Lasmini_haobam__](https://instagram.com/Lasmini_haobam__)\n\n"
                "✨ Stay tuned for more giveaways & tricks!\n"
                "#TeamTasmina ❤️",
                parse_mode='Markdown'
            )
            context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "📥 New Follower Request:\n\n"
                    f"👤 Name: {escape_markdown(full_name, version=2)} (ID: `{tg_id}`)\n"
                    f"📸 Username: `{escape_markdown(state['username'], version=2)}`\n"
                    f"🔢 Followers Wanted: {state['followers']}"
                ),
                parse_mode='MarkdownV2'
            )
            with user_data_lock:
                del user_data[user_id]
        except TelegramError as e:
            logger.error(f"Telegram API error in handle_messages: {e}")
            update.message.reply_text("⚠️ An error occurred. Please try again later.")

def cancel(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if get_user_data(user_id):
        with user_data_lock:
            del user_data[user_id]
        update.message.reply_text("✅ Request cancelled. Use /start to begin again.")
    else:
        update.message.reply_text("ℹ️ No active request to cancel.")

def main():
    keep_alive()
    try:
        updater = Updater(BOT_TOKEN)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("cancel", cancel))
        dp.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
        dp.add_handler(CallbackQueryHandler(button_callback))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_messages))
        updater.start_polling()
        logger.info("Bot started polling")
        updater.idle()
    except Exception as e:
        logger.error(f"Bot startup error: {e}")

if __name__ == '__main__':
    main()
