from aiogram import types, executor
from aiogram.dispatcher.filters import Command
from create_bot import *
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import logging
from pygsheets.exceptions import WorksheetNotFound, SpreadsheetNotFound

logging.basicConfig(level = logging.INFO)

user_data = {}
admin_gmail = 'gleb.iv@cataffs.com'
class SheetNotFound(Exception): pass

class RegistrationStates(StatesGroup):
    TYPE = State()
    NAME = State()
    DESCRIPTION = State()
    SOURCE = State()
    PHOTO = State()
    VOICE = State()
    GMAIL = State()

async def update_table(user_data: dict, user_id: int, email: str = None):
    sheet_name = str(user_id + 222)
    try:
        spreadsheet = gc.open(sheet_name)
        sheet = spreadsheet.worksheet()
        if email:
            if email == admin_gmail:
                spreadsheet.share(admin_gmail, 'writer')
            else:
                spreadsheet.share(email, 'writer')
                spreadsheet.share(admin_gmail, 'writer')
        sheet = spreadsheet.worksheet('index', 1 if user_data['contact_type'] == 'Целевые' else 0)
        row_data = [list(user_data.values())]
        last_row = len(sheet.get_all_values(include_tailing_empty = False, include_tailing_empty_rows = False))
        sheet.insert_rows(last_row, len(row_data), row_data)
        return sheet.url
    except SpreadsheetNotFound:
        spreadsheet = gc.create(sheet_name)
        firts_sheet = spreadsheet.add_worksheet(title='Не целевые', index = 0)
        second_sheet = spreadsheet.add_worksheet(title='Целевые', index = 1)

        start_cols = [['Тип', 'Имя', 'Описания', 'Сорс', 'Фото', 'Войс']]
        firts_sheet.insert_rows(0, len(start_cols), start_cols)
        second_sheet.insert_rows(0, len(start_cols), start_cols)
        print(spreadsheet)
        raise SheetNotFound


@dp.message_handler(Command('start'), state = "*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    kb = types.ReplyKeyboardMarkup(
        [[
        types.KeyboardButton('Целевые'),
        types.KeyboardButton('Не целевые')
    ]], resize_keyboard = True
    )
    await message.answer("Введите тип контакта:", reply_markup = kb)
    await state.set_state(RegistrationStates.TYPE)


@dp.message_handler(lambda m: m.text in ('Целевые', 'Не целевые'), state = RegistrationStates.TYPE)
async def process_contact_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['contact_type'] = message.text
    await message.answer("Введите имя:")
    await state.set_state(RegistrationStates.NAME)


@dp.message_handler(state = RegistrationStates.NAME)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer("Введите описание:")
    await state.set_state(RegistrationStates.DESCRIPTION)


@dp.message_handler(state = RegistrationStates.DESCRIPTION)
async def process_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await message.answer("Введите источник (сорс):")
    await state.set_state(RegistrationStates.SOURCE)


@dp.message_handler(state = RegistrationStates.SOURCE)
async def process_source(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['source'] = message.text
    await message.answer("Скинте на фото:")
    await state.set_state(RegistrationStates.PHOTO) 


@dp.message_handler(state = RegistrationStates.PHOTO, content_types = types.ContentTypes.PHOTO)
async def process_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = await message.photo[-1].get_url()
    await message.answer("Введите голосовое сообщение (текст):")
    await state.set_state(RegistrationStates.VOICE)  


@dp.message_handler(state = RegistrationStates.GMAIL)
async def process_gamil(message: types.Message, state: FSMContext):
    url = await update_table(await state.get_data(), message.from_id, message.text)
    await message.answer(f'Записи сохранены.Посмотреть <a href="{url}">тут</a>')
    await state.finish() 


@dp.message_handler(state = RegistrationStates.VOICE)
async def process_voice(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['voice'] = message.text
        try:
            url = await update_table(data, message.from_id)
            await message.answer(f'Записи сохранены.Посмотреть <a href="{url}">тут</a>')
            await state.finish()
        except SheetNotFound:
            await message.answer('Введите свой gmail для доступа:')
            await state.set_state(RegistrationStates.GMAIL)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)