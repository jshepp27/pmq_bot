import telegram.constants
from telegram import (
    Update, InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove,
)

from telegram.ext import (
    filters,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
    ConversationHandler,
    Updater,

)
import logging
import os

# TODOs: Abstract Commands as module commands.py

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

import load_config
TOKEN = os.environ["TOKEN"]
logger.info(TOKEN)



FIRST, NEXT = range(2)

dates = {
    "11th November": "/Users/joshua_sheppard/PycharmProjects/pmqBot/data/pmqs_parsed_2022-11-30.jsonl",
    "7th December": "/Users/joshua_sheppard/PycharmProjects/pmqBot/data/pmqs_parsed_2022-12-07.jsonl",
    "14th December": "/Users/joshua_sheppard/PycharmProjects/pmqBot/data/pmqs_parsed_2022-12-14.jsonl"
}

options = [_ for _ in dates.keys()]
# print(options)
# print(options[0])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    inline_keyboard = [[
        InlineKeyboardButton(f"{options[0]}", callback_data=int(0)),
        InlineKeyboardButton(f"{options[1]}", callback_data=int(1)),
        InlineKeyboardButton(f"{options[2]}", callback_data=int(2)),
    ]]

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard
    )

    await update.message.reply_text("Please select PMQ:", reply_markup=reply_markup)

    return FIRST

import json
import time
async def first(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    query = update.callback_query
    await query.answer()

    pmq = options[int(query.data)]
    file = dates[pmq]

    context.user_data["count"] = int(0)
    count = context.user_data["count"]

    inline_keyboard = [[
        InlineKeyboardButton(f"Next", callback_data=str("NEXT")),
    ]]

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard
    )

    pmqs = [json.loads(_) for _ in open(file)]

    context.user_data["pmqs"] = pmqs

    questions = pmqs[count]["question"]["member"]
    responses = pmqs[count]["response"]["member"]

    member = pmqs[count]["member"]["title"]
    img = pmqs[count]["member"]["img_url"]

    #caption = f"<b>fuck you</b>"
    #await update.callback_query.message.reply_photo(photo=img, caption=caption, parse_mode="html")
    for _ in range(0, len(questions)):
        insert = f"<a>{img}</a>"
        await update.callback_query.message.reply_text(text=insert, parse_mode="html")

        #await update.callback_query.message.reply_text(f"*Member: * {member}\n\n{questions[_]}", parse_mode="Markdown")
        time.sleep(1)

        if _ < len(questions) - 1:
            await update.callback_query.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}", parse_mode="Markdown")
            time.sleep(1)

        else:
            await update.callback_query.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}", reply_markup=reply_markup, parse_mode="Markdown")

    return NEXT

async def next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    query = update.callback_query
    await query.answer()

    if query.data == "NEXT":

        context.user_data["count"] += 1
        count = context.user_data["count"]

        inline_keyboard = [[
            InlineKeyboardButton(f"Next", callback_data=str("NEXT")),
        ]]

        reply_markup = InlineKeyboardMarkup(
            inline_keyboard
        )

        pmqs = context.user_data["pmqs"]

        member = pmqs[count]["member"]["title"]
        img = pmqs[count]["member"]["img_url"]

        if member.startswith("Rt Hon Keir Starmer"):
            questions = pmqs[count]["question"]["opposition"]
            responses = pmqs[count]["response"]["opposition"]

        else:
            questions = pmqs[count]["question"]["member"]
            responses = pmqs[count]["response"]["member"]

        await update.callback_query.message.reply_photo(photo=img)

        for _ in range(0, len(questions)):
            await update.callback_query.message.reply_text(f"*Member: * {member}\n\n{questions[_]}", parse_mode="Markdown")
            time.sleep(1)

            if _ < len(questions) - 1:
                await update.callback_query.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}", parse_mode="Markdown")
                time.sleep(1)

            else:
                if count < len(pmqs) - 1:
                    await update.callback_query.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}", reply_markup=reply_markup, parse_mode="Markdown")

                else:
                    await update.callback_query.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}", parse_mode="Markdown")

        return NEXT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()

if __name__ == "__main__":

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states = {
            FIRST: [CallbackQueryHandler(first)],
            NEXT: [CallbackQueryHandler(next)]
        },
        fallbacks=[CommandHandler("cancel", cancel),
                   CommandHandler("start", start)]
    )

    app.add_handler(conv_handler)

    app.run_polling()
