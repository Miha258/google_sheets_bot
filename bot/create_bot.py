from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os, sys
import pygsheets
from aiogram.types import ParseMode


CREDENTIALS_FILE = './credentials.json'
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
bot_token = "6397347343:AAH2qdJ0ch-AB65FwX374pt5-_GROefQ4vw"

bot = Bot(token = bot_token, parse_mode = ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage = storage)

owner = '1'
storage = MemoryStorage()

def get_channel():
    return os.environ.get("TARGET_CHANNEL")

def set_channel(channel):
    os.environ["TARGET_CHANNEL"] = channel

gc = pygsheets.authorize(service_file=CREDENTIALS_FILE)