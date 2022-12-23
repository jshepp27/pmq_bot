from telegram import (
    Update, InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
)
import logging
import json
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

# Data Directories
dates = {
    "Wednesday 11th November": "/Users/joshua_sheppard/PycharmProjects/pmqBot/data/pmqs_parsed_2022-11-30.jsonl",
    "Wednesday 7th December": "/Users/joshua_sheppard/PycharmProjects/pmqBot/data/pmqs_parsed_2022-12-07.jsonl",
    "Wednesday 14th December": "/Users/joshua_sheppard/PycharmProjects/pmqBot/data/pmqs_parsed_2022-12-14.jsonl"
}

options = [_ for _ in dates.keys()]

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     start_text = open("./data/content/start.txt").read()
#     await context.bot.sendMessage(chat_id=update.effective_chat.id, text=start_text)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    context.user_data["callback"] = query.data

    await query.edit_message_text(text=f"Selected option: {query.data}")
    return FIRST

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    inline_keyboard = [[
        InlineKeyboardButton(f"{options[0]}", callback_data="0"),
        InlineKeyboardButton(f"{options[1]}", callback_data="1"),
        InlineKeyboardButton(f"{options[2]}", callback_data="2"),
    ]]
    reply_markup = InlineKeyboardMarkup(
        #reply_keyboard, one_time_keyboard=True, input_field_placeholder="Which PMQs?"
        inline_keyboard
    )

    await update.message.reply_text("Please select PMQ:", reply_markup=reply_markup)
    query = update.callback_query

#    return FIRST

import time
async def first_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    response = update.message.text
    #response = context.user_data["callback"]
    print(response)

    pmq = response
    file = dates[pmq]
    context.user_data["count"] = 0

    count = context.user_data["count"]
    print(count)

    pmqs = [json.loads(_) for _ in open(file)]
    context.user_data["pmqs"] = pmqs

    questions = pmqs[count]["question"]["member"]
    responses = pmqs[count]["response"]["member"]

    member = pmqs[count]["member"]["title"]

    inline_keyboard = [[
        InlineKeyboardButton(f"Next", callback_data="0"),
        InlineKeyboardButton(f"Back", callback_data="1"),
    ]]

    inline_markup = InlineKeyboardMarkup(
        inline_keyboard
    )

    for _ in range(0, len(questions)):
        await update.message.reply_text(f"*Member: * {member}\n\n{questions[_]}", parse_mode="Markdown")
        time.sleep(2)

        if _ < len(questions) - 1:
            await update.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}", parse_mode="Markdown")
            time.sleep(1)

        else:
            await update.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}", reply_markup=inline_markup, parse_mode="Markdown")

    return NEXT

# DONE: Present Debate Data: Member, Opposition, Imgs
# DONE: PM Response
# TODO: Control Presentation of Next
# TODO: Print 'Clap' Emoji, conditional on like or dislike
# TODO: Handel Likes
# TODO: Error Modes
# TODO: Rename as PMQ Bot
# TODO: Injest from ElasticSearch
# TODO: Write to Google Sheets

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    response = update.message.text

    inline_keyboard = [[
        InlineKeyboardButton(f"Next", callback_data="0"),
        InlineKeyboardButton(f"Back", callback_data="1"),
    ]]

    inline_markup = InlineKeyboardMarkup(
        inline_keyboard
    )

    if response == "Next":
        context.user_data["count"] += 1
        count = context.user_data["count"]

        pmqs = context.user_data["pmqs"]

        if count >= len(pmqs):
            return ConversationHandler.END

        question = pmqs[count]["question"]
        member = pmqs[count]["member"]["title"]

        if "opposition" in question:
            questions = pmqs[count]["question"]["opposition"]
            responses = pmqs[count]["response"]["opposition"]

            for _ in range(0, len(questions)):
                await update.message.reply_text(f"*Leader of the Opposition: * {member}\n\n{questions[_]}",
                                                parse_mode="Markdown")
                time.sleep(1)
                if _ < len(questions) - 1:
                    await update.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}", parse_mode="Markdown")
                    time.sleep(1)

                else:
                    await update.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}", reply_markup=inline_markup,
                                                    parse_mode="Markdown")


            return NEXT

        elif "member" in question:
            questions = pmqs[count]["question"]["member"]
            responses = pmqs[count]["response"]["member"]

            for _ in range(0, len(questions)):
                await update.message.reply_text(f"*Member: * {member}\n\n{questions[_]}", parse_mode="Markdown")
                time.sleep(1)

                if _ < len(questions) - 1:
                    if count == len(pmqs) - 1:
                        await update.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}", parse_mode="Markdown")
                        time.sleep(1)

                    else:
                        await update.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}",
                                                        reply_markup=inline_markup,
                                                        parse_mode="Markdown")

                else:
                    await update.message.reply_text(f"*Prime Minister: *\n\n{responses[_]}", reply_markup=inline_markup,
                                                    parse_mode="Markdown")

            return NEXT

    else:
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command")


app = ApplicationBuilder().token(TOKEN).build()

if __name__ == "__main__":
    #app.add_handler(CallbackQueryHandler(button))

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler("start", start)],
        states = {
            FIRST: [MessageHandler(filters.ALL,first_question)],
            NEXT: [MessageHandler(filters.TEXT, next_question)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)


    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    app.add_handler(unknown_handler)

    app.run_polling()






    #app.add_handler(CommandHandler("start", start))
    #app.add_handler(CommandHandler("search", search))
    #app.add_handler(CallbackQueryHandler(button))


# async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await update.message.reply_text(f'Hello {update.effective_user.first_name}')

# echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#
#     query = update.callback_query
#
#     await query.answer()
#     #context.user_data["pmq_date"] = dates[options[int(query.data)]]
#
#     pmq = dates[options[int(query.data)]]
#
#     await query.edit_message_text(text=f"Prime Minister Engagements: {options[int(query.data)]}")

