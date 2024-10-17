from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import crud_functions

api = 'незабудьтеубратьключ'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
button4 = KeyboardButton(text='Регистрация')
kb.add(button, button2, button3, button4)

kb_inline_buy = InlineKeyboardMarkup(resize_keyboard=True)
inline_button1 = InlineKeyboardButton(text='Product1', callback_data='product_buying')
inline_button2 = InlineKeyboardButton(text='Product2', callback_data='product_buying')
inline_button3 = InlineKeyboardButton(text='Product3', callback_data='product_buying')
inline_button4 = InlineKeyboardButton(text='Product4', callback_data='product_buying')
kb_inline_buy.add(inline_button1, inline_button2, inline_button3, inline_button4)

kb_inline = InlineKeyboardMarkup(resize_keyboard=True)
inline_button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
inline_button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_inline.add(inline_button)
kb_inline.add(inline_button2)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет, я бот, помогающий твоему здоровью', reply_markup=kb)

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию', reply_markup=kb_inline)

@dp.callback_query_handler(text=['calories'])
async def set_age(call):
    await call.message.answer('Введите свой возраст:', reply_markup=kb)
    await call.answer()
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = int(message.text)
    await message.answer('Введите свой рост:', reply_markup=kb)
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['growth'] = int(message.text)
    await message.answer('Введите свой вес:', reply_markup=kb)
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['weight'] = int(message.text)
        age = data['age']
        growth = data['growth']
        weight = data['weight']

    calories = (10 * weight) + (6.25 * growth) - (5 * age) + 5

    await message.answer(f'Ваша норма калорий: {calories} ккал в день.', reply_markup=kb)
    await state.finish()

@dp.callback_query_handler(text=['formulas'])
async def get_formulas(call):
    await call.message.answer('calories = (10 * weight) + (6.25 * growth) - (5 * age) + 5')
    await call.answer()

@dp.message_handler(text='Купить')
async def get_buying_list(message):
    products = crud_functions.get_all_products()
    for product in products:
        title, description, price = product
        await message.answer(f'Название: {title} | Описание: {description} | Цена: {price}')
        image_path = f'file/{title}.png'
        if image_path:
            with open(image_path, 'rb') as photo:
                await message.answer_photo(photo=photo)
        await message.answer('Выберите продукт для покупки:', reply_markup=kb_inline_buy)

@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()

@dp.message_handler(text='Регистрация')
async def sign_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    username = message.text
    if crud_functions.is_included(username):
        await message.answer('Пользователь существует, введите другое имя:')
    else:
        async with state.proxy() as data:
            data['username'] = username
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = int(message.text)
        username = data['username']
        email = data['email']
        age = data['age']
        crud_functions.add_user(username, email, age)
    await message.answer('Регистрация успешно завершена!', reply_markup=kb)
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)