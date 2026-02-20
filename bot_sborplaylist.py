import asyncio
from io import BytesIO
import zipfile
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = "7536037949:AAFxlTovfRi0Vnxl8Pftr9OrqRnDdvzW0eQ"
bot = Bot(token=TOKEN)
dp = Dispatcher()

class CollectState(StatesGroup):
    waiting_audio = State()

audio_files = []

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵Собрать",callback_data="collect")],
        [InlineKeyboardButton(text="ℹ️Помощь",callback_data="help")]
    ])

def collect_menu(count):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ГотовZIP("+str(count)+")",callback_data="make_zip")]
    ])

@dp.message(CommandStart())
async def start(msg: types.Message):
    await msg.answer("🎧Упаковщик",reply_markup=main_menu())

@dp.callback_query(F.data=="help")
async def show_help(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("📋1@vkmusic2Найди3Скачай4Перешли",reply_markup=main_menu())

@dp.callback_query(F.data=="collect")
async def start_collect(callback: types.CallbackQuery,state: FSMContext):
    global audio_files
    audio_files=[]
    await state.set_state(CollectState.waiting_audio)
    await callback.answer()
    await callback.message.answer("✅Сбор!Пересылай@vkmusic_bot",reply_markup=collect_menu(0))

@dp.message(F.audio,CollectState.waiting_audio)
async def save_audio(msg: types.Message,state: FSMContext):
    global audio_files
    try:
        audio_files.append(msg.audio.file_id)
        count=len(audio_files)
        await msg.answer("✅Сохранено:"+str(count),reply_markup=collect_menu(count))
    except:
        await msg.answer("❌Ошибка")

@dp.callback_query(F.data=="make_zip",CollectState.waiting_audio)
async def make_zip(callback: types.CallbackQuery,state: FSMContext):
    global audio_files
    await callback.answer()
    
    if not audio_files:
        await callback.message.answer("❌Нетфайлов",reply_markup=main_menu())
        await state.clear()
        return
    
    await callback.message.answer("⏳СоздаюZIP...")
    
    try:
        zip_buffer=BytesIO()
        with zipfile.ZipFile(zip_buffer,"w")as zf:
            zf.writestr("info.txt","Плейлист:"+str(len(audio_files))+"треков")
            for i,file_id in enumerate(audio_files,1):
                zf.writestr(f"track{i}.txt","file_id:"+file_id)
        zip_buffer.seek(0)
        await bot.send_document(
            callback.message.chat.id,
            document=types.BufferedInputFile(zip_buffer.read(),filename="🎧плейлист.zip")
        )
        await callback.message.answer("🎉Готово:"+str(len(audio_files))+"треков",reply_markup=main_menu())
        audio_files=[]
        await state.clear()
    except Exception as e:
        print("ZIP error:",e)
        await callback.message.answer("❌ZIPошибка",reply_markup=main_menu())
        await state.clear()

async def main():
    print("🎧Запущен!")
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())