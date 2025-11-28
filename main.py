import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
GROQ_KEY = os.getenv('AI_TOKEN')

client = Groq(api_key=GROQ_KEY)

MODEL = "llama-3.1-8b-instant"

user_chatgpt_mode = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Student", callback_data="student")],
        [InlineKeyboardButton("IT-Technologies", callback_data="it_tech")],
        [InlineKeyboardButton("Contacts", callback_data="contacts")],
        [InlineKeyboardButton("ChatGPT prompt", callback_data="chatgpt")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f'Hi {user.first_name}!\n\nChoose a command:', reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "back":
        user_chatgpt_mode[user_id] = False
        keyboard = [
            [InlineKeyboardButton("Student", callback_data="student")],
            [InlineKeyboardButton("IT-Technologies", callback_data="it_tech")],
            [InlineKeyboardButton("Contacts", callback_data="contacts")],
            [InlineKeyboardButton("ChatGPT prompt", callback_data="chatgpt")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose a command:", reply_markup=reply_markup)

    elif query.data == "student":
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Student Information\n\nName: Roskoshenko Maksym\nGroup: IM-24",
            reply_markup=reply_markup,
        )

    elif query.data == "it_tech":
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "IT Technologies\n\nMain stack: Backend Java", reply_markup=reply_markup
        )

    elif query.data == "contacts":
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Contacts\n\nTelegram: @deadsnxw", reply_markup=reply_markup
        )

    elif query.data == "chatgpt":
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "ChatGPT mode activated!\n\nSend me your prompt:", reply_markup=reply_markup
        )
        user_chatgpt_mode[user_id] = True

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    if not text:
        await update.message.reply_text("Пустое сообщение — напиши, пожалуйста, текст.")
        return

    if user_chatgpt_mode.get(user_id):
        try:
            try:
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            except Exception:
                pass

            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": text}],
            )

            reply_text = ""
            try:
                reply_text = response.choices[0].message.content
            except Exception:
                reply_text = str(response)

            if not reply_text:
                print("Response is empty. Error:", response)
                await update.message.reply_text("AI returned an empty response")
                return

            for i in range(0, len(reply_text), 4096):
                chunk = reply_text[i : i + 4096]
                await update.message.reply_text(chunk)

            print(f"Response ({user_id}): {reply_text[:200]}...")

        except Exception as e:
            print("Error while calling Groq API:", repr(e))
            await update.message.reply_text(f"⚠️ Error: {e}")
    else:
        print("User is not in ChatGPT mode.")
        await update.message.reply_text("Please use /start to choose a command.")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))

    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
