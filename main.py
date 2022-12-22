"""
PMQs Bot to Search and Stream PMQs and Topics

"""

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # for reply keyboard (sends message)
import os
import logging
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import load_config
TOKEN = os.environ["TOKEN"]

# Initilaize Bot
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

answers = []

welcome_interaction = KeyboardButton("I'm felling good 👍")
welcome_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(welcome_interaction)

import json
file = "data/pmqs_parsed_2022-12-07.jsonl"
pmqs_ = (json.loads(_) for _ in open(file))

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.answer('Hello you rascal! ', reply_markup=welcome_kb)

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    pmq = next(pmqs_)
    question = pmq["question"]["member"]
    if len(question) > 1:
        q1 = question[0]
        q2 = question[1]
    else:
        q1 = question[-1]
    await message.answer(q1)

if __name__ == "__main__":
    logger.info(">>> Running pmq-bot ... ")
    executor.start_polling(dp, skip_updates=True)

