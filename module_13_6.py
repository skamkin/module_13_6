from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


api = '782....'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Рассчитать'),
                                     KeyboardButton(text="Информация")]],
                           resize_keyboard=True)

inline_choice = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories'),
                 InlineKeyboardButton('Формула расчета', callback_data='formulas')]])

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите интересующий вас пункт', reply_markup=inline_choice)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Формула расчета: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.')


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст в годах:')
    print('Введите свой возраст в годах:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост в см:')
    print('Введите свой рост в см:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес в кг:')
    print('Введите свой вес в кг:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    calories = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age'])
    await message.answer(calories)
    await state.finish()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=menu)

@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)